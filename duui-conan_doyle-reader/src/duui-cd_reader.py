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

from cd_reader_utils import read_cd_file, parse_cd_file
from cd_reader_utils import Token, Negation, Sentence, Pos, Lemma


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
    lemmas: Optional[List[Lemma]] = None
    poss: Optional[List[Pos]] = None
    sentences: Optional[List[Sentence]] = None
    negations: Optional[List[Negation]] = None

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
    cd_version: float = 0.1


# settings + cache
settings = Settings()


# Start fastapi
# TODO openapi types are not shown?
# TODO self host swagger files: https://fastapi.tiangolo.com/advanced/extending-openapi/#self-hosting-javascript-and-css-for-docs
app = FastAPI(
    openapi_url="/openapi.json",
    docs_url="/api",
    redoc_url=None,
    title="CD-NegationReader",
    description="CD(Conan and Doyle)-NegationReader for TTLab TextImager DUUI",
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
        "outputs": [
                    "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"
                    "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma",
                    "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence",
                    "de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS",
                    "org.texttechnologylab.annotation.negation.CompleteNegation"]
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
        annotator_name=f"CD-NegationReader-Version: {settings.cd_version}",
        version=str(settings.cd_version),
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

        docs = []
        res = read_cd_file(buffer)
        for key in res:
            docs.append((key, res[key]))

        for doc in docs:
            QUEUE.put(doc)
        return InitResponse(accepted=True,
                            n_docs=QUEUE.qsize())

    else:
        return InitResponse(accepted=False,
                            n_docs=QUEUE.qsize())

# Process request from DUUI
@app.post("/v1/process")
def process(request: DUUIRequest) -> DUUIResponse: # negations, paras, tokens, doc_name, " ".join(text)
    if not QUEUE.empty():
        current_doc = QUEUE.get()
        # print(*current_doc, sep="\n")
        content = parse_cd_file(current_doc[1])  # tuple[list[Sentence], list[Token], list[Lemma], list[Pos], list[Negation], str]
        return DUUIResponse(doc_name=current_doc[0],
                            sofa_str=content[5],
                            token=content[1],
                            negations=content[4],
                            lemmas=content[2],
                            poss=content[3],
                            sentences=content[0],
                            accepted=True)
    else:
        return DUUIResponse(accepted=False)



if __name__ == "__main__":
    uvicorn.run("duui-cd_reader:app", host="0.0.0.0", port=9714, workers=1)