from pydantic import BaseModel
from typing import Union, Literal

class Personality(BaseModel):
    openness: int
    conscientiousness: int
    extraversion: int
    agreeableness: int
    neuroticism: int

class InitialRelationship(BaseModel):
    ape1: str
    ape2: str
    relationship: str

class ApeSocialInfo(BaseModel):
    name: str
    age: int
    gender: Union[Literal["male"], Literal["female"]]
    role: str

class SocialBlueprint(BaseModel):
    apes: list[ApeSocialInfo]
    relationships: list[InitialRelationship]

class ApeDetails(BaseModel):
    facts: list[str]
    opinions: list[str]
