import os
import shutil
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Union

from .annotations import Negation, Token, Lemma, Pos, Sentence
from .file_io import find_cd_files


BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../.."))


def parse_cd_file(content: str):
    total_tokens = []
    total_sentences = []
    total_pos = []
    total_lemmas = []
    total_negs = []
    offset = 0
    sofa = []
    for sentence in content.split("\n\n"):
        if sentence.strip() != "":
            cue = None
            neg = Negation(cue=Token(begin=-1, end=-1))
            scope = []
            event = []

            sent = []
            sent_offset = offset
            for token in sentence.strip().split("\n"):
                annotations = token.strip().split("\t")
                sent.append(annotations)
                # print(annotations)
            text = " ".join([anno[3] for anno in sent])
            sofa.append(text)
            if sent[0][7] == "***":
                for tok in sent:
                    total_tokens.append(Token(begin=offset, end=offset+len(tok[3])))
                    total_lemmas.append(Lemma(begin=offset, end=offset+len(tok[3]), value=tok[4]))
                    total_pos.append(Pos(begin=offset, end=offset + len(tok[3]), value=tok[5]))
                    offset += len(tok[3]) + 1
            else:
                for tok in sent:
                    target_tok = Token(begin=offset, end=offset + len(tok[3]))
                    total_tokens.append(target_tok)
                    total_lemmas.append(Lemma(begin=offset, end=offset + len(tok[3]), value=tok[4]))
                    total_pos.append(Pos(begin=offset, end=offset + len(tok[3]), value=tok[5]))


                    if tok[7] != "_":
                        if cue is None:
                            cue = [offset, offset + len(tok[3])]
                        elif isinstance(cue, list):
                            cue[1] = offset + len(tok[3])
                        else:
                            pass
                    else:
                        if isinstance(cue, list):
                            cue = Token(begin=cue[0], end=cue[1])
                            neg.cue = cue
                            total_tokens.append(cue)
                        else:
                            pass

                    if tok[8] != "_":
                        scope.append(target_tok)
                    if tok[9] != "_":
                        event.append(target_tok)
                    offset += len(tok[3]) + 1
                if neg.cue.begin != -1 and neg.cue.end != -1:
                    if scope:
                        neg.scope = scope
                    if event:
                        neg.event = event
                    total_negs.append(neg)
            total_sentences.append(Sentence(begin=sent_offset, end=offset - 1))


    return total_sentences, total_tokens, total_lemmas, total_pos, total_negs, " ".join(sofa)


def read_cd_file(zip_bytes: Union[bytes, BytesIO]):
    temp_dir = Path(tempfile.mkdtemp())
    if isinstance(zip_bytes, bytes):
        zip_bytes = BytesIO(zip_bytes)
    with zipfile.ZipFile(zip_bytes, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    result = dict()
    find_cd_files(Path(temp_dir), result, dict(), temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)
    return result
