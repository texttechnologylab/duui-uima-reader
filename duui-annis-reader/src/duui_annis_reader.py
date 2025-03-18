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
from functools import lru_cache
from annis_utils import *
from api_utils import *


QUEUE = DocumentQueue()


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
    token: Optional[List[Token]] = None
    plain_text: Optional[List[PlainText]] = None
    lang: Optional[List[Lang]] = None
    lemma: Optional[List[Lemma]] = None
    document: Optional[List[Document]] = None # TODO is this really needed???
    verse: Optional[List[Verse]] = None
    line: Optional[List[Line]] = None
    writer: Optional[List[Writer]] = None
    pos: Optional[List[Pos]] = None  # Part of speech, for example
    clause: Optional[List[Clause]] = None
    inflection_class_lemma: Optional[List[InflectionClassLemma]] = None
    subchapter: Optional[List[Subchapter]] = None
    posLemma: Optional[List[PosLemma]] = None
    inflection: Optional[List[Inflection]] = None
    line_m: Optional[List[Line_m]] = None
    page: Optional[List[Page]] = None
    rhyme: Optional[List[Rhyme]] = None
    translation: Optional[List[Translation]] = None
    chapter: Optional[List[Chapter]] = None
    inflectionClass: Optional[List[InflectionClass]] = None
    edition: Optional[List[Edition]] = None

    sofa_str: Optional[str] = None
    meta_data: Optional[List[DocumentMetaData]] = None

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
    annis_version: float = 3.3


# settings + cache
settings = Settings()


# Start fastapi
# TODO openapi types are not shown?
# TODO self host swagger files: https://fastapi.tiangolo.com/advanced/extending-openapi/#self-hosting-javascript-and-css-for-docs
app = FastAPI(
    openapi_url="/openapi.json",
    docs_url="/api",
    redoc_url=None,
    title="annisReader",
    description="ANNIS Reader for TTLab TextImager DUUI",
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
communication = "communication.lua"
with open(communication, 'rb') as f:
    communication = f.read().decode("utf-8")


# Load the predefined typesystem that is needed for this annotator to work
typesystem_filename = 'dkpro-core-types.xml'
with open(typesystem_filename, 'rb') as f:
    typesystem = load_typesystem(f)


# Get input / output of the annotator
@app.get("/v1/details/input_output")
def get_input_output() -> JSONResponse:
    json_item = {
        "inputs": [],
        "outputs": [
                    "org.texttechnologylab.annotation.annis.Language",
                    "org.texttechnologylab.annotation.annis.Verse",
                    "org.texttechnologylab.annotation.annis.PosLemma",
                    "org.texttechnologylab.annotation.annis.Rhyme",
                    "org.texttechnologylab.annotation.annis.Translation",
                    "org.texttechnologylab.annotation.annis.Inflection",
                    "org.texttechnologylab.annotation.annis.InflectionClass",
                    "org.texttechnologylab.annotation.annis.InflectionClassLemma",
                    "org.texttechnologylab.annotation.annis.Clause",
                    "org.texttechnologylab.annotation.annis.Variation",
                    "org.texttechnologylab.annotation.annis.Writer",
                    "org.texttechnologylab.annotation.annis.Chapter",
                    "org.texttechnologylab.annotation.annis.SubChapter",
                    "org.texttechnologylab.annotation.annis.Page",
                    "org.texttechnologylab.annotation.annis.Line",
                    "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma",
                    "de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS",
                    "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token",
                    "de.tudarmstadt.ukp.dkpro.core.api.metadata.type.MetaDataStringField"
                    ]
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
        annotator_name=f"ANNIS-Version: {settings.annis_version} Reader",
        version=str(settings.annis_version),
        implementation_lang="Python",
    )
    return documentation

@app.post("/v1/init")
async def init_annis_reader(file: UploadFile = File(...)) -> InitResponse:
    if not QUEUE.has_next():
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

        documents = dict()
        files_from_zip_in_bytes(buffer.read(), documents)
        # print(documents)

        for document_id in documents:
            # print(document_id)
            node_annis = documents[document_id]['node.annis']
            node_annotation_annis = documents[document_id]['node_annotation.annis']
            corpus_annis = documents[document_id]['corpus.annis']
            corpus_annotation_annis = documents[document_id]['corpus_annotation.annis']
            text_annis = documents[document_id]['text.annis']
            annis_corpus = ANNISExtractor.from_file_like(node_file=node_annis,
                                                         node_annotation_file=node_annotation_annis,
                                                         corpus_file=corpus_annis,
                                                         corpus_annotation_file=corpus_annotation_annis,
                                                         text_file=text_annis)
            apd, tpd = annis_corpus.extract_annotations(*annis_corpus.extract_text())

            try:
                mpd = annis_corpus.extract_doc_metadata(annis_corpus.extract_corpus_metadata(), annis_corpus.extract_corpus_doc_mapping())
            except Exception as e:
                print(e)
                mpd = None

            QUEUE.fill(annotations_per_doc=apd,
                       text_per_document=tpd,
                       meta_data_per_document=mpd) # TODO add metadata

        return InitResponse(accepted=True,
                            n_docs=QUEUE.get_count())

    else:
        return InitResponse(accepted=False,
                            n_docs=QUEUE.get_count())


# Process request from DUUI
@app.post("/v1/process")
def process(request: DUUIRequest) -> DUUIResponse:
    if QUEUE.has_next():
        current_doc = QUEUE.next()
        sorted_annotations = {value: [] for key, value in mapping.items()}
        for annotation in current_doc.annotations:
            current_anno = construct_annotation(annotation)
            sorted_annotations[type(current_anno)].append(current_anno)
        if current_doc.meta_data is not None:
            for meta_data_anno in current_doc.meta_data:
                current_anno = construct_annotation(meta_data_anno)
                sorted_annotations[type(current_anno)].append(current_anno)

        return DUUIResponse(plain_text=sorted_annotations[PlainText],
                            lang=sorted_annotations[Lang],
                            lemma=sorted_annotations[Lemma],
                            document=sorted_annotations[Document],
                            verse=sorted_annotations[Verse],
                            line=sorted_annotations[Line],
                            writer=sorted_annotations[Writer],
                            pos=sorted_annotations[Pos],
                            clause=sorted_annotations[Clause],
                            inflection_class_lemma=sorted_annotations[InflectionClassLemma],
                            subchapter=sorted_annotations[Subchapter],
                            posLemma=sorted_annotations[PosLemma],
                            inflection=sorted_annotations[Inflection],
                            line_m=sorted_annotations[Line_m],
                            page=sorted_annotations[Page],
                            rhyme=sorted_annotations[Rhyme],
                            translation=sorted_annotations[Translation],
                            chapter=sorted_annotations[Chapter],
                            inflectionClass=sorted_annotations[InflectionClass],
                            edition=sorted_annotations[Edition],
                            token=sorted_annotations[Token],
                            sofa_str=current_doc.text,
                            meta_data=sorted_annotations[DocumentMetaData],
                            accepted=True
                            )
    else:
        return DUUIResponse(accepted=False)



if __name__ == "__main__":
    uvicorn.run("duui_annis_reader:app", host="0.0.0.0", port=9714, workers=1)