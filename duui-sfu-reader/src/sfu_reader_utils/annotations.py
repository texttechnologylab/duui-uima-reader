from typing import Optional, List, Tuple, Union, Dict
from pydantic import BaseModel

# tok
class Token(BaseModel):
    begin: int
    end: int

# sent
class Sentence(BaseModel):
    begin: int
    end: int

# para
class Paragraph(BaseModel):
    begin: int
    end: int

# neg
class Negation(BaseModel):
    negType: Optional[str] = None
    cue: Token
    event: Optional[List[Token]] = None
    focus: Optional[List[Token]] = None
    scope: Optional[List[Token]] = None
    xscope: Optional[List[Token]] = None