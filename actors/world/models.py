from pydantic import BaseModel

class CreateTerritory(BaseModel):
    name: str
    description: str
    resources: list[str]


class CreateWorld(BaseModel):
    description: str
    territories: list[CreateTerritory]


