import io
import os
import sys
from typing import List, Tuple
import requests
import pandas as pd
from tqdm import tqdm
import json

from annis_utils import files_from_zip_in_bytes, ANNISExtractor
from api_utils import DocumentQueue
from duui_annis_reader import DUUIRequest


BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../.."))

def parse_xls():
    def replace_all(s: str, replacements: Tuple[str, str]) -> str:
        for i in replacements:
            s = s.replace(i[0], i[1])
        return s

    # Load the Excel file
    file_path = f"{BP}/data/2sent_ctx/PositiveBasesofOHGBNDAs.xlsx"
    xls = pd.ExcelFile(file_path)
    # Load the sheet into a DataFrame
    df = xls.parse(sheet_name=xls.sheet_names[0])

    # Convert the DataFrame to a JSON structure
    json_data = df.to_dict(orient="records")

    target = {"pos_base": [], "pos_base_clean": [], "neg_base": [], "trans": []}
    for row in json_data:
        target["pos_base"].append(row["Positive Bases of OHG BNDAs"])
        target["neg_base"].append(row["OHG BNDAs (Splett)"])
        target["trans"].append(row["BNDAs im Nhd (Liste A02)"])
    with open(f"{BP}/data/2sent_ctx/target.json", "w", encoding="utf-8") as f:
        json.dump(target, f, ensure_ascii=False, indent=4)
    return target

def test_multiple_corpora():
    target_pos_base = parse_xls()
    queue = DocumentQueue()
    test_file = f"{BP}/data/2sent_ctx/ahd.zip"

    file = open(test_file, 'rb')
    documents = dict()
    files_from_zip_in_bytes(file, documents)
    # print(documents)

    for document_id in documents:
        # print(document_id)
        try:
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
                mpd = annis_corpus.extract_doc_metadata(annis_corpus.extract_corpus_metadata(),
                                                        annis_corpus.extract_corpus_doc_mapping())
            except Exception as e:
                print(e)
                mpd = None

            queue.fill(annotations_per_doc=apd,
                       text_per_document=tpd,
                       meta_data_per_document=mpd)
        except Exception as e:
            print(documents[document_id]['node.annis'])
            print(e)
            print("he")
            pass
        # TODO test


        while queue.has_next():
            current_doc = queue.next()
            # print(current_doc.text)
            # print(current_doc.meta_data)
            for word in target_pos_base["pos_base"]:
                if "â" in word or "ô" in word or "î" in word:
                    if word in current_doc.text:
                        print(current_doc.annotations)
                        print(word)

            # print(current_doc.annotations)


if __name__ == '__main__':
    test_multiple_corpora()
    # parse_xls()