import csv
import os
import shutil
import tempfile
import zipfile
from io import BytesIO, StringIO
from pathlib import Path
from typing import Union
from nltk.tokenize import TreebankWordTokenizer

from .annotations import Negation, Token, Sentence
from .file_io import find_bs_files


BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../.."))


def tokenize_with_offsets_advanced(text):
    tokenizer = TreebankWordTokenizer()
    # Get spans (start, end) along with tokens
    spans = list(tokenizer.span_tokenize(text))
    return spans


def parse_bs_file(content: str):
    total_tokens = []
    total_sentences = []
    total_negs = []
    offset = 0
    sofa = []

    csv_file = StringIO(content)

    # Parse the CSV
    reader = csv.DictReader(csv_file)  # Use DictReader to get rows as dictionaries
    for row in reader:
        # row keys = sentence, sentence_id, cue_span, scope_span
        sofa.append(row["sentence"])
        for token in tokenize_with_offsets_advanced(row["sentence"]):
            total_tokens.append(Token(begin=offset + token[0], end=offset + token[1]))
        total_sentences.append(Sentence(begin=offset, end=offset + len(row["sentence"])))

        if row["cue_span"] != "NaN":
            try:
                cues = eval(row["cue_span"])
                # print(cues)
                cue = Token(begin=offset + cues[0][0], end=offset + cues[0][1])
                scope = []
                if row["scope_span"] != "NaN":
                    try:
                        scopes = eval(row["scope_span"])
                        scope.append(Token(begin=offset + scopes[0], end=offset + scopes[1]))
                    except:
                        print("scope issue")
                neg = Negation(cue=cue)
                if scope:
                    neg.scope = scope
                total_negs.append(neg)
                total_tokens.append(cue)
                for sc in scope:
                    total_tokens.append(sc)
            except:
                print("cue issue")
        offset += len(row["sentence"]) + 1

    return total_sentences, list(set(total_tokens)), total_negs, " ".join(sofa)


def read_bs_file(zip_bytes: Union[bytes, BytesIO]):
    temp_dir = Path(tempfile.mkdtemp())
    if isinstance(zip_bytes, bytes):
        zip_bytes = BytesIO(zip_bytes)
    with zipfile.ZipFile(zip_bytes, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    result = dict()
    find_bs_files(Path(temp_dir), result, dict(), temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)
    return result
