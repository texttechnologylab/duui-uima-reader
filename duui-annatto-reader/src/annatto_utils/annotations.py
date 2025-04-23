from typing import Optional, List, Tuple, Union, Dict
from pydantic import BaseModel


# Lemma
class Lemma(BaseModel):
    begin: int
    end: int
    value: str

# Pos (Part of Speech)
class Pos(BaseModel):
    begin: int
    end: int
    value: str

# Token
class Token(BaseModel):
    begin: int
    end: int
    value: str
