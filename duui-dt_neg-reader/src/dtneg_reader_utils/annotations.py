from typing import Optional, List, Tuple, Union, Dict
from pydantic import BaseModel

# tok
class Token(BaseModel):
    begin: int
    end: int

    def __str__(self):
        return str(self.begin) + str(self.end) + "token"

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return self.begin == other.begin and self.end == other.end

# sent
class Sentence(BaseModel):
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