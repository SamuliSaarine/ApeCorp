from pydantic import BaseModel
from typing import Union, Literal

class Personality(BaseModel):
    openness: int
    conscientiousness: int
    extraversion: int
    agreeableness: int
    neuroticism: int

class CreateApe(BaseModel):
    name: str
    age: int
    gender: Union[Literal["male"], Literal["female"]]
    role: str
    facts: list[str]
    opinions: list[str]
    relationships: dict[str, str]
