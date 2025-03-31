from typing import Optional, List, Tuple, Union, Dict
from pydantic import BaseModel

# Lang
class Token(BaseModel):
    begin: int
    end: int

# Lemma
class Paragraph(BaseModel):
    begin: int
    end: int

# Document
class Negation(BaseModel):
    negType: Optional[str] = None
    cue: Token
    event: Optional[List[Token]] = None
    focus: Optional[List[Token]] = None
    scope: Optional[List[Token]] = None
    xscope: Optional[List[Token]] = None