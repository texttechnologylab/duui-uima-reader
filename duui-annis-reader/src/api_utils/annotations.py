from typing import Optional, List, Tuple, Union, Dict
from pydantic import BaseModel

# Lang
class Lang(BaseModel):
    begin: int
    end: int
    value: str

# Lemma
class Lemma(BaseModel):
    begin: int
    end: int
    value: str

# Document
class Document(BaseModel):
    begin: int
    end: int
    value: str

# Verse
class Verse(BaseModel):
    begin: int
    end: int
    value: str

# Line
class Line(BaseModel):
    begin: int
    end: int
    value: str

# Writer
class Writer(BaseModel):
    begin: int
    end: int
    value: str

# Pos (Part of Speech)
class Pos(BaseModel):
    begin: int
    end: int
    value: str

# Clause
class Clause(BaseModel):
    begin: int
    end: int
    value: str

# InflectionClassLemma
class InflectionClassLemma(BaseModel):
    begin: int
    end: int
    value: str

# Subchapter
class Subchapter(BaseModel):
    begin: int
    end: int
    value: str

# PosLemma
class PosLemma(BaseModel):
    begin: int
    end: int
    value: str

# Inflection
class Inflection(BaseModel):
    begin: int
    end: int
    value: str

# Line_m
class Line_m(BaseModel):
    begin: int
    end: int
    value: str

# Page
class Page(BaseModel):
    begin: int
    end: int
    value: str

# Rhyme
class Rhyme(BaseModel):
    begin: int
    end: int
    value: str

# Translation
class Translation(BaseModel):
    begin: int
    end: int
    value: str

# Chapter
class Chapter(BaseModel):
    begin: int
    end: int
    value: str

# InflectionClass
class InflectionClass(BaseModel):
    begin: int
    end: int
    value: str

# Edition
class Edition(BaseModel):
    begin: int
    end: int
    value: str


# Token
class Token(BaseModel):
    begin: int
    end: int
    value: str


# PlainText
class PlainText(BaseModel):
    begin: int
    end: int
    value: str

# DocumentMetaData
class DocumentMetaData(BaseModel):
    key: str
    value: str

mapping = {'lang': Lang,
           'lemma': Lemma,
           'document': Document,
           'verse': Verse,
           'line': Line,
           'writer': Writer,
           'pos': Pos,
           'clause': Clause,
           'inflectionClassLemma': InflectionClassLemma,
           'subchapter': Subchapter,
           'posLemma': PosLemma,
           'inflection': Inflection,
           'line_m': Line_m,
           'page': Page,
           'rhyme': Rhyme,
           'translation': Translation,
           'chapter': Chapter,
           'inflectionClass': InflectionClass,
           'edition': Edition,
           'token': Token,
           'text': PlainText,
           'metadata': DocumentMetaData
           }


def construct_annotation(annotation: Tuple[str, Dict[str, Union[str, int]]]):
    """
    Store annotations
    :param annotation:
    :return:
    """
    # print(annotation)
    return mapping[annotation[0]](**annotation[1])


if __name__ == "__main__":
    new_dict = {value: [] for key, value in mapping.items()}
    print(new_dict)

    b = Lemma(begin=2, end=3, value="d")
    print(b)

    new_dict[type(b)].append(b)

    print(new_dict)

    print(new_dict[Lemma])