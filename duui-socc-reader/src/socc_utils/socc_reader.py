import csv
import os
import shutil
import tempfile
import zipfile
from io import BytesIO, StringIO
from pathlib import Path
from typing import Union, Dict, Tuple, List
from pydantic import BaseModel

from .annotations import Paragraph, Token, Negation
from .file_io import find_folder_pathlib, find_tsv_files


BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../.."))


def convert_tsv(doc_name: str, tsv: str) -> Tuple[List[Negation], List[Paragraph], List[Token], str, str]:
    rd = csv.reader(StringIO(tsv), delimiter="\t", quotechar='"')
    text = []
    text_dict = {}
    tokens = []
    paras = []
    negations = []
    max_idx = 0
    cue = []
    focus = {}
    scope = {}
    xscope = {}

    sent_begin = 0
    sent_end = 0
    sent_begins = False
    for row in rd:
        if row:
            if "#Text=" in row[0]:
                text.append(row[0].lstrip("#Text="))
                sent_begins = True
                if sent_begin != 0 or sent_end != 0:
                    paras.append(Paragraph(begin=sent_begin, end=sent_end))
                if cue:
                    for idx, cu in enumerate(cue):
                        if focus:
                            foc = focus[list(focus.keys())[0]]
                            del focus[list(focus.keys())[0]]
                        else:
                            foc = None
                        if scope:
                            sco = scope[list(scope.keys())[0]]
                            del scope[list(scope.keys())[0]]
                        else:
                            sco = None
                        if xscope:
                            xsco = xscope[list(xscope.keys())[0]]
                            del xscope[list(xscope.keys())[0]]
                        else:
                            xsco = None
                        negations.append(Negation(cue=cu, scope=sco, xscope=xsco, focus=foc))
                    if focus:
                        for key in focus:
                            negations[-1].focus.append(focus[key])
                        focus = {}
                    if scope:
                        for key in scope:
                            negations[-1].scope.append(scope[key])
                        focus = {}
                    if xscope:
                        for key in xscope:
                            negations[-1].xscope.append(xscope[key])
                        focus = {}
                cue = []
            else:
                if len(row) >= 2:
                    if "-" in row[0] and "-" in row[1]:
                        tok_start, tok_end = int(row[1].split("-")[0]), int(row[1].split("-")[1])
                        if sent_begins:
                            sent_begin = tok_start
                            sent_begins = False
                        sent_end = tok_end
                        tok = Token(begin=tok_start, end=tok_end)
                        tokens.append(tok)
                        tok_form = row[2]
                        if tok_end > max_idx:
                            max_idx = tok_end
                        for tok_char_idx, char_idx in enumerate(range(tok_start, tok_end)):
                            # print(tok_form[tok_char_idx], tok_start, tok_end)
                            try:
                                text_dict[char_idx] = tok_form[tok_char_idx]
                            except:
                                text_dict[char_idx] = " "

                        if len(row) >= 4:
                            if row[3] != "_" and row[3] != "":
                                annos = row[3].split("|")
                                for anno in annos:
                                    if "NEG" in anno:
                                        cue.append(tok)
                                    elif "SCOPE" in anno:
                                        if scope.get(anno):
                                            scope[anno].append(tok)
                                        else:
                                            scope[anno] = [tok]
                                    elif "XSCOPE" in anno:
                                        if xscope.get(anno):
                                            xscope[anno].append(tok)
                                        else:
                                            xscope[anno] = [tok]
                                    elif "FOCUS" in anno:
                                        if focus.get(anno):
                                            focus[anno].append(tok)
                                        else:
                                            focus[anno] = [tok]
                else:
                    pass
    paras.append(Paragraph(begin=sent_begin, end=sent_end))
    if cue:
        for idx, cu in enumerate(cue):
            if focus:
                foc = focus[list(focus.keys())[0]]
                del focus[list(focus.keys())[0]]
            else:
                foc = None
            if scope:
                sco = scope[list(scope.keys())[0]]
                del scope[list(scope.keys())[0]]
            else:
                sco = None
            if xscope:
                xsco = xscope[list(xscope.keys())[0]]
                del xscope[list(xscope.keys())[0]]
            else:
                xsco = None
            negations.append(Negation(cue=cu, scope=sco, xscope=xsco, focus=foc))
        if focus:
            for key in focus:
                negations[-1].focus.append(focus[key])
            focus = {}
        if scope:
            for key in scope:
                negations[-1].scope.append(scope[key])
            focus = {}
        if xscope:
            for key in xscope:
                negations[-1].xscope.append(xscope[key])
            focus = {}
    sofa_str = ""
    print(text_dict)
    for i in range(max_idx):
        try:
            sofa_str += text_dict[i]
        except:
            sofa_str += " "

    # return negations, paras, tokens, doc_name, " ".join(text)
    return negations, paras, tokens, doc_name, sofa_str


def read_socc_negation(zip_bytes: Union[bytes, BytesIO], target_folder_name: str):
    # Find the target folder in the zip data
    temp_dir = Path(tempfile.mkdtemp())
    found_folder = find_folder_pathlib(zip_bytes, target_folder_name, temp_dir)
    result = dict()
    if found_folder:
        if os.path.isdir(os.path.join(found_folder, "curation")):
            # print(f"Found target folder at: {found_folder}")
            # print(os.listdir(found_folder))
            # Find all .tsv files and their contents
            find_tsv_files(os.path.join(found_folder, "curation"), result)

    shutil.rmtree(temp_dir, ignore_errors=True)
    return result




