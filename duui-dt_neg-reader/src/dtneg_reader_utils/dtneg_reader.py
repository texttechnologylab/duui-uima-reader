import bisect
import os
import shutil
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Union, Tuple, List, Any

from nltk import TreebankWordTokenizer

from .annotations import Negation, Token, Sentence
from .file_io import find_dtneg_files


BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../.."))


def get_delimiter_offsets(s):
    # Define delimiter pairs: (opening, closing, type)
    delimiter_pairs = [('<<', '>>', '<<>>'), ('{', '}', '{}'), ('[', ']', '[]')]

    # Maps for quick lookup
    opening_to_type = {open: type for open, close, type in delimiter_pairs}
    closing_to_type = {close: type for open, close, type in delimiter_pairs}

    # Stack to track nested delimiters
    stack = []
    # Final string without delimiters
    final_string = ""
    # List to store delimiter sets for each character in final_string
    char_delimiters = []

    # Parse the string
    i = 0
    while i < len(s):
        found = False
        # Check each delimiter pair
        for open, close, type in delimiter_pairs:
            # Opening delimiter
            if s[i:i + len(open)] == open:
                stack.append(type)
                i += len(open)
                found = True
                break
            # Closing delimiter
            elif s[i:i + len(close)] == close:
                if not stack or stack[-1] != type:
                    raise ValueError("Mismatched delimiters", s)
                stack.pop()
                i += len(close)
                found = True
                break
        # Character is not part of a delimiter
        if not found:
            final_string += s[i]
            # Record current delimiters for this character
            char_delimiters.append(set(stack))
            i += 1

    # Find offsets for each delimiter type
    from collections import defaultdict
    offsets = defaultdict(list)
    delimiter_types = [pair[2] for pair in delimiter_pairs]

    for type in delimiter_types:
        in_range = False
        start = 0
        for j in range(len(final_string)):
            if type in char_delimiters[j]:
                if not in_range:
                    in_range = True
                    start = j
            elif in_range:
                offsets[type].append((start, j))
                in_range = False
        if in_range:
            offsets[type].append((start, len(final_string)))

    # Format result as list of (delimiter_type, content, (start, end))
    result = []
    for type in offsets:
        for start, end in offsets[type]:
            content = final_string[start:end]
            result.append((type, content, (start, end)))

    # Return final string and offsets
    return final_string, result


def tokenize_with_offsets_advanced(text):
    tokenizer = TreebankWordTokenizer()
    # Get spans (start, end) along with tokens
    spans = list(tokenizer.span_tokenize(text))
    return spans


def adjust_offsets(original_string: str,
                   token_offsets: List[Tuple[int, int]],
                   replacements: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[int, int]]]:

    # Apply replacements and track changes
    for old, new in replacements:
        while old in original_string:
            pos_start = original_string.index(old)
            pos_end = pos_start + len(old)
            original_string = original_string.replace(old, new, 1)
            delta = len(new) - len(old)
            for idx, token in enumerate(token_offsets):
                if token[0] < pos_start and token[1] <= pos_start:
                    pass
                elif token[0] >= pos_end and token[1] > pos_end:
                    token_offsets[idx] = (token[0] + delta, token[1] + delta)
                else:
                    token_offsets[idx] = (token[0], token[1] + delta)

    return original_string, token_offsets


def fix_abbr(answer: str, annos: List[Tuple[str, str, Tuple[int, int]]]) -> Tuple[str, List[Tuple[str, str, Tuple[int, int]]]]:
    repl = [(" n't ", " not "), (" ca ", " can "), (" wo ", " will "), (" sha  ", " shall ")]
    offsets = [anno[2] for anno in annos]
    answer, offsets = adjust_offsets(answer, offsets, replacements=repl)
    for idx in range(len(annos)):
        annos[idx] = (annos[idx][0], annos[idx][1], offsets[idx])
    return answer, annos

def parse_dtneg_file(content: str):
    total_tokens = []
    total_sentences = []
    total_negs = []
    offset = 0
    sofa = []
    sent_set = list(set(list(content.split("-----------------"))))

    for sent in sent_set:
        try:
            question = None
            answer = None
            cue = None
            scope = []
            focus = []
            if sent.strip() == "":
                continue
            for sent_part in sent.split("\n"):
                if "QUESTION:" in sent_part:
                    question = sent_part.split("QUESTION:")[-1].strip()
                if "ANNOTATEDANSWER:" in sent_part:
                    answer = sent_part.split("ANNOTATEDANSWER:")[-1].strip()
            question = question.replace("[", "").replace("{", "").replace("}", "").replace("<", "").replace(">", "").replace("]", "")
            for token in tokenize_with_offsets_advanced(question):
                total_tokens.append(Token(begin=offset + token[0], end=offset + token[1]))
            total_sentences.append(Sentence(begin=offset, end=offset + len(question)))
            offset += len(question) + 1
            sofa.append(question)

            answer, annos = fix_abbr(*get_delimiter_offsets(answer))
            for anno in annos:
                anno_tok = Token(begin=offset + anno[2][0], end=offset + anno[2][1])
                total_tokens.append(anno_tok)
                if anno[0] == "<<>>":
                    cue = anno_tok
                elif anno[0] == "{}":
                    focus.append(anno_tok)
                elif anno[0] == "[]":
                    scope.append(anno_tok)
            if cue is not None:
                neg = Negation(cue=cue)
                if scope:
                    neg.scope = scope
                if focus:
                    neg.focus = focus
                total_negs.append(neg)

            answer = answer.replace("n't", "not").replace(" ca ", " can ").replace(" wo ", "will").replace(" sha  ", "shall")
            for token in tokenize_with_offsets_advanced(answer):
                answer_tok = Token(begin=offset + token[0], end=offset + token[1])
                if answer_tok not in total_tokens:
                    total_tokens.append(answer_tok)
            total_sentences.append(Sentence(begin=offset, end=offset + len(answer)))
            offset += len(answer) + 1
            sofa.append(answer)
        except Exception as e:
            print(e)

    return total_sentences, total_tokens, total_negs, " ".join(sofa)


def read_dtneg_file(zip_bytes: Union[bytes, BytesIO]):
    temp_dir = Path(tempfile.mkdtemp())
    if isinstance(zip_bytes, bytes):
        zip_bytes = BytesIO(zip_bytes)
    with zipfile.ZipFile(zip_bytes, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    result = dict()
    find_dtneg_files(Path(temp_dir), result, dict(), temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)
    return result
