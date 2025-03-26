import _csv
import csv
import zipfile
from io import BytesIO, StringIO
from typing import Union, List, Any

from se_utils.annotations import Sentence, Token, Lemma, Pos


def read_file_as_byte(file_ref: str, zip_ref: zipfile.ZipFile) -> BytesIO:
    """
    read zip file as bytes and return them in file like byte buffer.
    :param file_ref:
    :param zip_ref:
    :return:
    """
    with zip_ref.open(file_ref) as file:
        file_contents = file.read()  # Read file contents as bytes
        return BytesIO(file_contents)


def find_all_csv_files(zip_ref_lst: List[str]):

    found_files = [ref for ref in zip_ref_lst if ".csv" in ref]
    return found_files


def files_from_zip_in_bytes(zip_bytes: Union[bytes, BytesIO], csv_files: list):

    # Use BytesIO to treat the byte data as a file-like object
    # with BytesIO(zip_bytes) as byte_io:
    if isinstance(zip_bytes, bytes):
        byte_io = BytesIO(zip_bytes)
        del zip_bytes
    else:
        byte_io = zip_bytes

    with zipfile.ZipFile(byte_io, 'r') as zip_ref:
        # List all file names in the zip file
        # print("Files in the ZIP archive:", zip_ref.namelist())
        target_csv_files = find_all_csv_files(zip_ref.namelist())
        csv_files.extend([read_file_as_byte(file, zip_ref) for file in target_csv_files])

        for file in zip_ref.namelist():
            if ".zip" in file:
                with zip_ref.open(file) as zf:
                    file_contents = zf.read()
                files_from_zip_in_bytes(file_contents, csv_files)


def convert_bytesIO_to_csv(bytes_io: BytesIO):
    return csv.reader(StringIO(bytes_io.getvalue().decode("utf-8")))


def import_se_docs(zip_bytes: Union[bytes, BytesIO]) -> List[dict]:
    csv_bytes_lst = []
    files_from_zip_in_bytes(zip_bytes, csv_bytes_lst)
    csv_lst = []
    for file in csv_bytes_lst:
        csv_lst.append(convert_bytesIO_to_csv(file))
    del csv_bytes_lst
    corpora = {}
    for idx, file in enumerate(csv_lst):
        corpus_name, docs = import_csv(file, idx)
        if corpora.get(corpus_name):
            corpora[corpus_name] = corpora[corpus_name] | docs
        else:
            corpora[corpus_name] = docs

    docs = []
    for corpus_key in corpora.keys():
        for doc_key in corpora[corpus_key].keys():
            corpora[corpus_key][doc_key]["doc_id"] = doc_key
            corpora[corpus_key][doc_key]["corp_id"] = corpus_key
            docs.append(corpora[corpus_key][doc_key])
    return docs


def import_csv(csv_file, cdx: int):
    corpus_name = "unk"
    docs = dict()
    id_dict = dict()
    for idx, row in enumerate(csv_file):
        if idx == 0 and "corpus" in " ".join(row):
            corpus_name = row[-1]
        elif idx > 4:
            if docs.get(row[0]) is not None:
                id_dict[row[0]] += 1
                docs[row[0] + f"_{id_dict[row[0]]}.{cdx}"] = import_doc(row[1:])
            else:
                id_dict[row[0]] = 1
                docs[row[0] + f"_{id_dict[row[0]]}.{cdx}"] = import_doc(row[1:])

            # print(row[1])
    return corpus_name, docs


def import_doc(doc: List[str]):
    processed_doc = []
    sent_strings = doc[0].split("</s><s>")
    for sent_string in sent_strings:
        processed_doc.append(sent_string.split())

    tokens = []
    sents = []
    poss = []
    lemmas = []
    sofa_str = []

    offset = 0
    for sent in processed_doc:
        sent_start = offset

        for token in sent:
            annotations = token.split("/")

            if len(annotations) == 5:
                pass
            else:
                if annotations[0] == "that":
                    del annotations[3]
                elif '<s>' in annotations:
                    continue
                elif len(annotations) == 8:
                    annotations = ["/", "/", annotations[4], annotations[5], "/" + annotations[-1]]
                elif "[number]" in annotations and len(annotations) == 6:
                    annotations = ["/".join(annotations[:2]), annotations[2], annotations[3], annotations[4], annotations[5]]
                else:
                    print(annotations)
                    print(token)
                    print(sent)
                    continue
            tok_start = offset

            tok = annotations[0]
            lemma = annotations[1]
            pos_fine = annotations[2]
            pos_coarse = annotations[3]

            offset += (len(tok) + 1)
            sofa_str.append(tok)
            tok_end = offset

            tokens.append(Token(begin=tok_start, end=tok_end, value=tok))
            lemmas.append(Lemma(begin=tok_start, end=tok_end, value=lemma))
            poss.append(Pos(begin=tok_start, end=tok_end, coarse_value=pos_coarse, fine_value=pos_fine))
        sent_end = offset
        sents.append(Sentence(begin=sent_start, end=sent_end))
    #print(sents)
    #print(lemmas)
    #print(poss)

    return {"token": tokens, "lemmas": lemmas, "pos": poss, "sents": sents, "sofa": " ".join(sofa_str)}


if __name__ == "__main__":
    test_file = "/home/staff_homes/lehammer/Documents/work/sketch_engine_reader/data/se_example.zip"

    with open(test_file, 'rb') as f:
        zb = f.read()

    res = import_se_docs(zb)
    print(res[0])

