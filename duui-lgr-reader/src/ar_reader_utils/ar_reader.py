import bisect
import copy
import os
import re
import shutil
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Union, Tuple, List, Any
from TexSoup import TexSoup
from nltk import TreebankWordTokenizer

from .annotations import Token, Sentence, Negation, UCEMetaData, DLink, ADLink, DALink
from .file_io import find_ar_files


BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../.."))


def tokenize_with_offsets_advanced(text):
    tokenizer = TreebankWordTokenizer()
    # Get spans (start, end) along with tokens
    spans = list(tokenizer.span_tokenize(text))
    return spans

def to_small_caps(text):
    # Replace A-Z with small caps if available
    small_caps_map = {
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ꜰ',
        'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ',
        'M': 'ᴍ', 'N': 'ɴ', 'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ',
        'S': 'ꜱ', 'T': 'ᴛ', 'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'х',
        'Y': 'ʏ', 'Z': 'ᴢ'
    }
    return ''.join(small_caps_map.get(c.upper(), c) for c in text)

def split_at_xg(text):
    # Use regex to split at \ followed by any single character and then g.
    return re.split(r'\\.{1}g\.', text)

def replace_textsc_with_small_caps(text):
    # Replace each \textsc{...} with its small caps version
    return re.sub(r'\\textsc\{([^}]*)\}', lambda m: to_small_caps(m.group(1)), text)


def remove_first_occurrence_after_index(text, substring, start_index):
    # Find the first occurrence of substring starting from start_index
    index = text.find(substring, start_index)

    # If the substring is found
    if index != -1:
        # Remove the first occurrence of substring
        text = text[:index] + text[index + len(substring):]

    return text


def get_section_content(text):
    # Regular expression to match \section{...}
    match = re.search(r'\\section\{(.*?)\}', text)

    if match:
        return match.group(1)  # Return the content inside the braces
    else:
        return None  # Return None if no match is found

def get_subsection_content(text):
    # Regular expression to match \section{...}
    match = re.search(r'\\subsection\{(.*?)\}', text)

    if match:
        return match.group(1)  # Return the content inside the braces
    else:
        return None  # Return None if no match is found

def pad_right(s: str, total_length: int) -> str:
    return s.ljust(total_length)

def parse_ar_file(content: str):
    content = replace_textsc_with_small_caps(content)
    content = content.split("\ex.")
    docs = []
    doc_id = 0
    participient = "unk"
    subsection = "unk"
    for category in content:
        if "\\section" in category:
            participient = get_section_content(copy.deepcopy(category)).split("Participant:")[-1].strip().replace("/", "&")
        if "\\subsection" in category:
            subsection = get_subsection_content(copy.deepcopy(category)).replace("/", "&")
        found = False
        total_tokens = []
        total_sentences = []
        offset = 0
        sofa = []
        cues = []
        for example in split_at_xg(category):
            example =example.split("\\\\")
            cue = None
            if len(example) == 3:
                found = True
                sent = example[0].lstrip().split("\n")[0].replace("[A:]", "").replace("[Q:]", "")
                annos = example[1].lstrip().split("\n")[0].replace("[A:]", "").replace("[Q:]", "")
                translation = example[2].lstrip().split("\n")[0].replace("[A:]", "").replace("[Q:]", "")

                while "\\textbf" in sent:
                    neg_offset = sent.index("\\textbf")
                    sent = remove_first_occurrence_after_index(sent, "\\textbf{", neg_offset)
                    neg_offset_end = sent.index("}", neg_offset)
                    cue = (neg_offset + offset, offset + neg_offset + (neg_offset_end - neg_offset))
                    sent = remove_first_occurrence_after_index(sent, "}", neg_offset)

                t_sent = [_ for _ in sent.split(" ") if _ != ""]
                t_annos = [_ for _ in annos.split(" ") if _ != ""]
                sent, annos = [], []
                neg_offset_change = 0
                for idx in range(len(t_sent)):
                    try:
                        a_tok = t_annos[idx]
                    except:
                        sent.append(s_tok)
                        continue
                    s_tok = t_sent[idx]
                    if len(s_tok) > len(a_tok):
                        a_tok = pad_right(a_tok, len(s_tok))
                    elif len(s_tok) < len(a_tok):
                        s_tok = pad_right(s_tok, len(a_tok))
                        neg_offset_change += (len(a_tok) - len(s_tok))
                    else:
                        pass
                    sent.append(s_tok)
                    annos.append(a_tok)
                sent = " ".join(sent)
                annos = " ".join(annos)
                if cue is not None:
                    cue_tok = Token(begin=cue[0] + neg_offset_change, end=cue[1] + neg_offset_change)
                    cues.append(cue_tok)
                    total_tokens.append(cue_tok)

                sofa.append(sent)
                sofa.append(annos)
                sofa.append(translation)
                sofa.append("\n")
                total_sentences.append(Sentence(begin=offset, end=offset + len(sent)))
                offset += len(sent) + 1
                total_sentences.append(Sentence(begin=offset, end=offset + len(annos)))
                offset += len(annos) + 1
                total_sentences.append(Sentence(begin=offset, end=offset + len(translation)))
                offset += len(translation) + 1
                offset += 2
        if found:
            doc_id += 1
            total_negations = [Negation(cue=cue) for cue in cues]
            docs.append((f"{doc_id}_{participient}_{subsection}", total_sentences, total_tokens, total_negations, "\n".join(sofa)))


    return docs


def parse_ar_file_for_UCE(content: str, id_key: str):
    content = replace_textsc_with_small_caps(content)
    content = content.split("\ex.")
    docs = []
    doc_id = 0
    participient = "unk"
    subsection = "unk"
    for category in content:
        if "\\section" in category:
            participient = get_section_content(copy.deepcopy(category)).split("Participant:")[-1].strip().replace("/", "&")
        if "\\subsection" in category:
            subsection = get_subsection_content(copy.deepcopy(category)).replace("/", "&")
        found = False
        total_tokens = []
        total_tokens_base = []

        total_sentences = []
        total_sentences_gloss = []
        total_sentences_translation = []
        total_sentences_base = []

        offset = 0
        offset_gloss = 0
        offset_translation = 0
        offset_base = 0

        sofa = []
        sofa_gloss = []
        sofa_translation = []
        sofa_base = []
        cues = []
        cues_base = []

        link_id = 0
        for example in split_at_xg(category):
            example =example.split("\\\\")
            cue = None
            if len(example) == 3:
                found = True
                sent = example[0].lstrip().split("\n")[0].replace("[A:]", "").replace("[Q:]", "")
                annos = example[1].lstrip().split("\n")[0].replace("[A:]", "").replace("[Q:]", "")
                translation = example[2].lstrip().split("\n")[0].replace("[A:]", "").replace("[Q:]", "")

                while "\\textbf" in sent:
                    neg_offset = sent.index("\\textbf")
                    sent = remove_first_occurrence_after_index(sent, "\\textbf{", neg_offset)
                    neg_offset_end = sent.index("}", neg_offset)
                    cue = (neg_offset + offset, offset + neg_offset + (neg_offset_end - neg_offset))
                    cue_base = (neg_offset + offset_base, offset_base + neg_offset + (neg_offset_end - neg_offset))
                    sent = remove_first_occurrence_after_index(sent, "}", neg_offset)

                t_sent = [_ for _ in sent.split(" ") if _ != ""]
                t_annos = [_ for _ in annos.split(" ") if _ != ""]
                sent, annos = [], []
                neg_offset_change = 0
                for idx in range(len(t_sent)):
                    try:
                        a_tok = t_annos[idx]
                    except:
                        sent.append(s_tok)
                        continue
                    s_tok = t_sent[idx]
                    if len(s_tok) > len(a_tok):
                        a_tok = pad_right(a_tok, len(s_tok))
                    elif len(s_tok) < len(a_tok):
                        s_tok = pad_right(s_tok, len(a_tok))
                        neg_offset_change += (len(a_tok) - len(s_tok))
                    else:
                        pass
                    sent.append(s_tok)
                    annos.append(a_tok)
                sent = " ".join(sent)
                annos = " ".join(annos)
                if cue is not None:
                    cue_tok = Token(begin=cue[0] + neg_offset_change, end=cue[1] + neg_offset_change)
                    cue_base_tok = Token(begin=cue_base[0] + neg_offset_change, end=cue_base[1] + neg_offset_change)
                    cues.append(cue_tok)
                    cues_base.append(cue_base_tok)
                    total_tokens.append(cue_tok)
                    total_tokens_base.append(cue_base_tok)

                sofa.append(sent)
                sofa_base.append(sent)
                sofa.append(annos)
                sofa_gloss.append(annos)
                sofa.append(translation)
                sofa_translation.append(translation)
                sofa.append("\n")
                sofa_base.append("\n")
                sofa_gloss.append("\n")
                sofa_translation.append("\n")
                total_sentences.append(Sentence(begin=offset, end=offset + len(sent)))
                total_sentences_base.append(Sentence(begin=offset_base, end=offset_base + len(sent)))
                offset_base += len(sent) + 1
                offset += len(sent) + 1
                total_sentences.append(Sentence(begin=offset, end=offset + len(annos)))
                total_sentences_gloss.append(Sentence(begin=offset_gloss, end=offset_gloss + len(annos)))
                offset_gloss += len(annos) + 1
                offset += len(annos) + 1
                total_sentences.append(Sentence(begin=offset, end=offset + len(translation)))
                total_sentences_translation.append(Sentence(begin=offset_translation, end=offset_translation + len(translation)))
                offset_translation += len(translation) + 1
                offset += len(translation) + 1

                offset_translation += 2
                offset_gloss += 2
                offset_base += 2
                offset += 2

        if found:
            doc_id += 1
            comb_doc_name = id_key + "_" + f"{doc_id}_{participient}_{subsection}"
            plain_doc_name = id_key + "_" + f"{doc_id}_{participient}_{subsection}_plaintext"
            gloss_doc_name = id_key + "_" + f"{doc_id}_{participient}_{subsection}_gloss"
            trans_doc_name = id_key + "_" + f"{doc_id}_{participient}_{subsection}_translation"
            # COMBINED
            da_links_comb, da_links_plain, da_links_gloss, da_links_trans = [], [], [], []
            ad_links_comb, ad_links_plain, ad_links_gloss, ad_links_trans = [], [], [], []
            plain_count, gloss_count, trans_count = 0, 0, 0
            for sent_idx, sent in enumerate(total_sentences):
                if sent_idx % 3 == 0:
                    ad_links_comb.append(
                        ADLink(fromX=sent, toY=plain_doc_name, link_type="plaintext_sent", id=plain_count))
                    da_links_comb.append(
                        DALink(fromX=plain_doc_name, toY=sent, link_type="plaintext_sent", id=plain_count))

                    ad_links_plain.append(
                        ADLink(fromX=total_sentences_base[plain_count], toY=comb_doc_name, link_type="plaintext_sent", id=plain_count))
                    da_links_plain.append(
                        DALink(fromX=comb_doc_name, toY=total_sentences_base[plain_count], link_type="plaintext_sent", id=plain_count))
                    plain_count += 1
                elif sent_idx % 3 == 1:
                    ad_links_comb.append(
                        ADLink(fromX=sent, toY=gloss_doc_name, link_type="gloss_sent", id=gloss_count))
                    da_links_comb.append(
                        DALink(fromX=gloss_doc_name, toY=sent, link_type="gloss_sent", id=gloss_count))

                    ad_links_gloss.append(
                        ADLink(fromX=total_sentences_gloss[gloss_count], toY=comb_doc_name, link_type="gloss_sent",
                               id=gloss_count))
                    da_links_gloss.append(
                        DALink(fromX=comb_doc_name, toY=total_sentences_gloss[gloss_count], link_type="gloss_sent",
                               id=gloss_count))
                    gloss_count += 1
                elif sent_idx % 3 == 2:
                    ad_links_comb.append(
                        ADLink(fromX=sent, toY=trans_doc_name, link_type="translation_sent", id=trans_count))
                    da_links_comb.append(
                        DALink(fromX=trans_doc_name, toY=sent, link_type="translation_sent", id=trans_count))

                    ad_links_trans.append(
                        ADLink(fromX=total_sentences_translation[trans_count], toY=comb_doc_name, link_type="translation_sent",
                               id=trans_count))
                    da_links_trans.append(
                        DALink(fromX=comb_doc_name, toY=total_sentences_translation[trans_count], link_type="translation_sent",
                               id=trans_count))
                    trans_count += 1

            dd_links = [DLink(fromX=comb_doc_name, toY=plain_doc_name, link_type="plaintext", id=link_id),
                     DLink(fromX=comb_doc_name, toY=gloss_doc_name, link_type="gloss", id=link_id + 1),
                     DLink(fromX=comb_doc_name, toY=trans_doc_name, link_type="translation", id=link_id + 2)]
            link_id += 3
            total_negations = [Negation(cue=cue) for cue in cues]
            uce_md_info = UCEMetaData(key="Participant", value=participient, value_type="ENUM")
            uce_md_type = UCEMetaData(key="Type", value=subsection, value_type="ENUM")
            uce_md_lang = UCEMetaData(key="Language", value=id_key, value_type="ENUM")
            uce_md_combined = UCEMetaData(key="View", value="combined", value_type="ENUM")
            docs.append((comb_doc_name, total_sentences, total_tokens, total_negations, "\n".join(sofa),
                         [uce_md_info, uce_md_type, uce_md_combined, uce_md_lang],
                         dd_links, ad_links_comb, da_links_comb))

            # PLAIN
            dd_links = [DLink(fromX=plain_doc_name, toY=comb_doc_name, link_type="plaintext", id=link_id)]
            link_id += 1
            total_negations_base = [Negation(cue=cue) for cue in cues_base]
            uce_md_base = UCEMetaData(key="View", value="plaintext", value_type="ENUM")
            docs.append((plain_doc_name, total_sentences_base, total_tokens_base, total_negations_base,
                         "\n".join(sofa_base),
                         [uce_md_info, uce_md_type, uce_md_base, uce_md_lang],
                         dd_links, ad_links_plain, da_links_plain))

            # GLOSS
            dd_links = [DLink(fromX=gloss_doc_name, toY=comb_doc_name, link_type="gloss", id=link_id)]
            link_id += 1
            uce_md_gloss = UCEMetaData(key="View", value="gloss", value_type="ENUM")
            docs.append((gloss_doc_name, total_sentences_gloss, [], [],
                         "\n".join(sofa_gloss),
                         [uce_md_info, uce_md_type, uce_md_gloss, uce_md_lang],
                         dd_links, ad_links_gloss, da_links_gloss))

            # TRANSLATION
            dd_links = [DLink(fromX=trans_doc_name, toY=comb_doc_name, link_type="translation", id=link_id)]
            link_id += 1
            uce_md_translation = UCEMetaData(key="View", value="translation", value_type="ENUM")
            docs.append((trans_doc_name, total_sentences_translation, [], [],
                         "\n".join(sofa_translation),
                         [uce_md_info, uce_md_type, uce_md_translation, uce_md_lang],
                         dd_links, ad_links_trans, da_links_trans))
    return docs


def read_ar_file(zip_bytes: Union[bytes, BytesIO]):
    temp_dir = Path(tempfile.mkdtemp())
    if isinstance(zip_bytes, bytes):
        zip_bytes = BytesIO(zip_bytes)
    with zipfile.ZipFile(zip_bytes, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    result = dict()
    find_ar_files(Path(temp_dir), result, dict(), temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)
    return result
