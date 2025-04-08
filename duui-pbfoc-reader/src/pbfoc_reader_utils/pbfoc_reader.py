import os
import shutil
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Union

from .annotations import Negation, Token, Pos, Sentence
from .file_io import find_pbfoc_files

BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../.."))


def parse_pbfoc_file(content: str):
    total_tokens = []
    total_sentences = []
    total_pos = []
    total_negs = []
    offset = 0
    sofa = []
    for sentence in content.split("\n\n"):
        if sentence.strip() != "":
            focus = []
            event = []
            cue = None
            sent_offset = offset

            for token in sentence.strip().split("\n"):
                token = [tok for tok in token.strip().split(" ") if tok != ""]
                token_form = " ".join(token)
                if token[4] == "n't":
                    token[4] = "not"
                token_obj = Token(begin=offset, end=offset + len(token[4]))
                sofa.append(token[4])
                total_tokens.append(token_obj)
                total_pos.append(Pos(begin=token_obj.begin, end=token_obj.end, value=token[6]))
                if cue is None and (token[4].lower() == "no" or token[4].lower() == "not" or token[4].lower() == "don't" or token[4].lower() == "never"):
                    cue = token_obj
                if "AM-NEG*" in token_form:
                    cue = token_obj
                if token[-1] == "FOCUS":
                    focus.append(token_obj)
                if token[-2] == "N":
                    event.append(token_obj)
                offset += (len(token[4]) + 1)

            if cue is not None:
                neg = Negation(cue=cue)
                if focus:
                    neg.focus = focus
                if event:
                    neg.event = event
                total_negs.append(neg)
            else:
                if focus or event:
                    print(sentence+ "\n\n")
            total_sentences.append(Sentence(begin=sent_offset, end=offset - 1))

    return total_sentences, total_tokens, total_pos, total_negs, " ".join(sofa)


def read_pbfoc_file(zip_bytes: Union[bytes, BytesIO]):
    temp_dir = Path(tempfile.mkdtemp())
    if isinstance(zip_bytes, bytes):
        zip_bytes = BytesIO(zip_bytes)
    with zipfile.ZipFile(zip_bytes, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    result = dict()
    find_pbfoc_files(Path(temp_dir), result, dict(), temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)
    return result