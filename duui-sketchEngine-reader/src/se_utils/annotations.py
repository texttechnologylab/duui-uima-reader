from typing import Optional, List, Tuple, Union, Dict
from pydantic import BaseModel

# Lang
class Token(BaseModel):
    begin: int
    end: int
    value: str

# Lemma
class Lemma(BaseModel):
    begin: int
    end: int
    value: str

# Sent
class Sentence(BaseModel):
    begin: int
    end: int

# Pos (Part of Speech)
class Pos(BaseModel):
    begin: int
    end: int
    coarse_value: str
    fine_value: str