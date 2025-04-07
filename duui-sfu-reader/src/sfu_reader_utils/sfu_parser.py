import os
import shutil
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO, FileIO, StringIO
from pathlib import Path
from typing import Union

from sfu_reader_utils.annotations import Token, Negation, Sentence, Paragraph
from sfu_reader_utils.file_io import find_xml_files, replace_illegal_xml_chars

BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../.."))


def parse_xml_file(file_content: Union[str]):
    # Parse the XML file
    root = ET.fromstring(file_content)

    time = root.find('TIME')

    # Process paragraphs
    paragraphs = root.findall('P')
    total_para_annos = []
    total_neg_annos = []
    total_tok_annos = []
    total_sent_annos = []
    text = []
    offset = 0
    for i, paragraph in enumerate(paragraphs, 1):
        para_offset_begin = offset
        sentences = paragraph.findall('SENTENCE')
        if sentences:  # Only process paragraphs with sentences
            for j, sentence in enumerate(sentences, 1):
                cue, cue_type, scope = None, "", []
                sent_offset_begin = offset
                # Iterate over all child elements in their original order
                for elem in sentence:
                    if elem.tag == 'W':
                        total_tok_annos.append(Token(begin=offset, end=offset + len(elem.text)))
                        text.append(elem.text)
                        offset += (len(elem.text) + 1)
                    elif elem.tag == 'cue':
                        if elem.get('type') == "negation":
                            cue_tok_begin = offset
                            cue_tok_end = offset
                            for w in elem.findall('W'):
                                total_tok_annos.append(Token(begin=offset, end=offset + len(w.text)))
                                text.append(w.text)
                                offset += (len(w.text) + 1)
                                cue_tok_end += (len(w.text) + 1)
                            cue_tok_end -= 1
                            cue_tok = Token(begin=cue_tok_begin, end=cue_tok_end)
                            if cue_tok in total_tok_annos:
                                pass
                            else:
                                total_tok_annos.append(cue_tok)
                            cue = cue_tok
                    elif elem.tag == 'xcope':
                        for sub_elem in elem:
                            if sub_elem.tag == 'W':
                                scope_tok = Token(begin=offset, end=offset + len(sub_elem.text))
                                total_tok_annos.append(scope_tok)
                                scope.append(scope_tok)
                                text.append(sub_elem.text)
                                offset += (len(sub_elem.text) + 1)
                            elif sub_elem.tag == "cue":
                                if sub_elem.get('type') == "negation":
                                    cue_tok_begin = offset
                                    cue_tok_end = offset
                                    for w in sub_elem.findall('W'):
                                        total_tok_annos.append(Token(begin=offset, end=offset + len(w.text)))
                                        text.append(w.text)
                                        offset += (len(w.text) + 1)
                                        cue_tok_end += (len(w.text) + 1)
                                    cue_tok_end -= 1
                                    cue_tok = Token(begin=cue_tok_begin, end=cue_tok_end)
                                    if cue_tok in total_tok_annos:
                                        pass
                                    else:
                                        total_tok_annos.append(cue_tok)
                                    cue = cue_tok
                    elif elem.tag == 'C':
                        for sub_elem in elem:
                            if sub_elem.tag == 'W':
                                total_tok_annos.append(Token(begin=offset, end=offset + len(sub_elem.text)))
                                text.append(sub_elem.text)
                                offset += (len(sub_elem.text) + 1)
                            elif sub_elem.tag == 'cue':
                                if sub_elem.get('type') == "negation":
                                    cue_tok_begin = offset
                                    cue_tok_end = offset
                                    for w in sub_elem.findall('W'):
                                        total_tok_annos.append(Token(begin=offset, end=offset + len(w.text)))
                                        text.append(w.text)
                                        offset += (len(w.text) + 1)
                                        cue_tok_end += (len(w.text) + 1)
                                    cue_tok_end -= 1
                                    cue_tok = Token(begin=cue_tok_begin, end=cue_tok_end)
                                    if cue_tok in total_tok_annos:
                                        pass
                                    else:
                                        total_tok_annos.append(cue_tok)
                                    cue = cue_tok
                            elif sub_elem.tag == 'xcope':
                                for w in sub_elem.findall('W'):
                                    scope_tok = Token(begin=offset, end=offset + len(w.text))
                                    total_tok_annos.append(scope_tok)
                                    scope.append(scope_tok)
                                    text.append(w.text)
                                    offset += (len(w.text) + 1)
                            else:
                                print(sub_elem)
                                print(f"    Unknown element ({sub_elem.tag}): {sub_elem.text}")
                    else:
                        # Handle any other unexpected tags
                        print(elem)
                        print(f"    Unknown element ({elem.tag}): {elem.text}")
                sent_offset_end = offset - 1
                total_sent_annos.append(Sentence(begin=sent_offset_begin, end=sent_offset_end))
                if cue is not None:
                    if not scope:
                        scope = None
                    total_neg_annos.append(Negation(cue=cue,
                                                    scope=scope))
        para_offset_end = offset - 1
        total_para_annos.append(Paragraph(begin=para_offset_begin, end=para_offset_end))

    return total_para_annos, total_sent_annos, total_tok_annos, total_neg_annos, replace_illegal_xml_chars(" ".join(text))


def read_sfu_negation(zip_bytes: Union[bytes, BytesIO]):
    temp_dir = Path(tempfile.mkdtemp())
    if isinstance(zip_bytes, bytes):
        zip_bytes = BytesIO(zip_bytes)
    with zipfile.ZipFile(zip_bytes, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    result = dict()
    find_xml_files(Path(temp_dir), result, dict(), temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)
    return result


def main():
    # Replace 'your_file.xml' with the path to your XML file
    file_path = "/home/staff_homes/lehammer/Documents/work/SFU_Reader/data/SFU_Review_Corpus_Negation_Speculation/BOOKS/no1done.xml"
    try:
        res = parse_xml_file(file_path)
        print(res[3])
        print(res[4])
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except ET.ParseError:
        print("Error: Invalid XML format.")


if __name__ == "__main__":
    zd = f"{BP}/data/SFU_Review_Corpus_Negation_Speculation.zip"  # Replace with your starting path
    # Example: Reading a zip file as bytes (replace with your actual bytes source)
    with open(zd, "rb") as f:  # Simulating bytes input
        zp = f.read()
    res = read_sfu_negation(zd)
    print(res["MOVIES_0"])
    print(parse_xml_file(res["MOVIES_0"])[3])