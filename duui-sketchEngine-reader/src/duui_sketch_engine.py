import os
from io import BytesIO
from typing import List, Optional, Any
import uvicorn
from cassis import *
from fastapi import FastAPI, Response, UploadFile, File, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import PlainTextResponse
from pydantic_settings import BaseSettings
from pydantic import BaseModel
from starlette.responses import JSONResponse
import queue
from functools import lru_cache

from se_utils import Pos, Lemma, Token, import_se_docs
from se_utils.annotations import Sentence

BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../.."))
QUEUE = queue.Queue()


class InitRequest(BaseModel):
    zip_file: bytes


class InitResponse(BaseModel):
    accepted: bool
    n_docs: Optional[int] = None


# Request sent by DUUI
# Note, this is transformed by the Lua script
class DUUIRequest(BaseModel):
    msg: Optional[str] = None

# Response of this annotator
# Note, this is transformed by the Lua script
class DUUIResponse(BaseModel):

    sofa_str: Optional[str] = None
    doc_name: Optional[str] = None

    token: Optional[List[Token]] = None
    lemma: Optional[List[Lemma]] = None
    pos: Optional[List[Pos]] = None
    sent: Optional[List[Sentence]] = None

    accepted: bool


# Documentation response
class TextImagerDocumentation(BaseModel):
    # Name of this annotator
    annotator_name: str
    # Version of this annotator
    version: str
    # Annotator implementation language (Python, Java, ...)
    implementation_lang: str


class Settings(BaseSettings):
    se_version: float = 0.1


# settings + cache
settings = Settings()


# Start fastapi
# TODO openapi types are not shown?
# TODO self host swagger files: https://fastapi.tiangolo.com/advanced/extending-openapi/#self-hosting-javascript-and-css-for-docs
app = FastAPI(
    openapi_url="/openapi.json",
    docs_url="/api",
    redoc_url=None,
    title="sketchEngineReader",
    description="SketchEngine Reader for TTLab TextImager DUUI",
    version="0.1",
    terms_of_service="https://www.texttechnologylab.org/legal_notice/",
    contact={
        "name": "TTLab Team",
        "url": "https://texttechnologylab.org",
        "email": "hammerla@em.uni-frankfurt.de",
    },
    license_info={
        "name": "AGPL",
        "url": "http://www.gnu.org/licenses/agpl-3.0.en.html",
    },
)

# Load the Lua communication script
communication = f"{BP}/src/communication.lua"
with open(communication, 'rb') as f:
    communication = f.read().decode("utf-8")


# Load the predefined typesystem that is needed for this annotator to work
typesystem_filename = f'{BP}/src/dkpro-core-types.xml'
with open(typesystem_filename, 'rb') as f:
    typesystem = load_typesystem(f)


# Get input / output of the annotator
@app.get("/v1/details/input_output")
def get_input_output() -> JSONResponse:
    json_item = {
        "inputs": [],
        "outputs": ["de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma",
                    "de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS",
                    "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"
                    "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence"]
    }

    json_compatible_item_data = jsonable_encoder(json_item)
    return JSONResponse(content=json_compatible_item_data)


# Get typesystem of this annotator
@app.get("/v1/typesystem")
def get_typesystem() -> Response:
    # TODO remove cassis dependency, as only needed for typesystem at the moment?
    xml = typesystem.to_xml()
    xml_content = xml.encode("utf-8")

    return Response(
        content=xml_content,
        media_type="application/xml"
    )


# Return Lua communication script
@app.get("/v1/communication_layer", response_class=PlainTextResponse)
def get_communication_layer() -> str:
    return communication


# Return documentation info
@app.get("/v1/documentation")
def get_documentation() -> TextImagerDocumentation:

    documentation = TextImagerDocumentation(
        annotator_name=f"SketchEngineReader-Version: {settings.se_version}",
        version=str(settings.se_version),
        implementation_lang="Python",
    )
    return documentation

@app.post("/v1/init")
async def init_se_reader(file: UploadFile = File(...)) -> InitResponse:
    if QUEUE.empty():
        try:
            # Accumulate the file content in memory
            buffer = BytesIO()
            while chunk := await file.read(1024 * 1024 * 10):  # 10 MB chunks
                buffer.write(chunk)

            # Reset pointer to the beginning before opening with ZipFile
            buffer.seek(0)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")
        finally:
            await file.close()

        docs = import_se_docs(buffer)
        for doc in docs:
            QUEUE.put(doc)
        return InitResponse(accepted=True,
                            n_docs=QUEUE.qsize())

    else:
        return InitResponse(accepted=False,
                            n_docs=QUEUE.qsize())

# Process request from DUUI
@app.post("/v1/process")
def process(request: DUUIRequest) -> DUUIResponse:
    if not QUEUE.empty():
        current_doc = QUEUE.get()
        return DUUIResponse(doc_name="".join([current_doc["corp_id"], current_doc["doc_id"]]),
                            sofa_str=current_doc["sofa"],
                            token=current_doc["token"],
                            lemma=current_doc["lemmas"],
                            sent=current_doc["sents"],
                            pos=current_doc["pos"],
                            accepted=True)
    else:
        return DUUIResponse(accepted=False)



if __name__ == "__main__":
    uvicorn.run("duui_sketch_engine:app", host="0.0.0.0", port=9714, workers=1)