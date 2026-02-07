from utils.get_model import get_model
from pydantic_ai import Agent
from pydantic import BaseModel
import asyncio

class Territory(BaseModel):
    name: str
    description: str
    resources: list[str]

class World(BaseModel):
    description: str
    territories: list[Territory]


system_prompt = """
You are a creative game master for a role playing game. The game is set in prehistoric times.
Your task is to create 3 options for a game world:
- These are not fantasy worlds, but its a choice of 3 diffent geographical locations on earth.
- Also since prehistoric is a long timerange, these may vary by exact time period.

Rules:
- The world should have at least 3 territories.
- Territories here are not huge areas of land, or biomes, but small zones
- 
- Each territory should have at least 3 resources.
"""

_agent = Agent(
    model=get_model("creative"),
    system_prompt=system_prompt,
    output_type=list[World]
)

async def run() -> list[World]:
    results = await _agent.run("Generate 3 world options.")
    return results.output