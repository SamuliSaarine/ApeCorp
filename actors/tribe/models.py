from pydantic import BaseModel

class CreateTribe(BaseModel):
    name: str
    territory: str
    background: str
    culture: str
    survival_strategy: str
    challenges: list[str]
    tribe_relations: dict[str, str]
