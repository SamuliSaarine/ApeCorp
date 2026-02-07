from utils.get_model import get_model
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from agents.map import World
import asyncio

class Tribe(BaseModel):
    name: str
    territory:str
    background: str
    culture: str
    survival_strategy: str
    challenges: list[str]
    tribe_relations: dict[str, str]

_system_prompt = """
Its prehistoric times. You are a creative game master for a role playing game.
Your task is to create 3 ape tribes based on the given world and following rules:
- In this game, prehistoric tribes operate like modern day corporations
- They have hierarchical structures with a C-level apes like CEA(Chief Executive Ape), middle-management, and workers 
- Each tribe has their own territory and unique strategy that answers the best their specific conditions
- They also have their own traditions, culture and history
- Relationships between other tribes might be cooperative, competive or neutral
"""

_agent = Agent(
    model=get_model("creative"),
    output_type=list[Tribe],
    system_prompt=_system_prompt
)

async def run(world: World) -> list[Tribe]:
    results = await _agent.run(world.model_dump_json(indent=2))
    return results.output
        