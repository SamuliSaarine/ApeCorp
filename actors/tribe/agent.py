from pydantic_world import get_model, load_md
from pydantic_ai import Agent
from .models import CreateTribe
from actors.world import instance as world
import os

_system_prompt = load_md("actors/tribe/system_prompt.md")

_agent = Agent(
    model=get_model("creative"),
    output_type=list[CreateTribe],
    system_prompt=_system_prompt
)

async def create_tribes() -> list[CreateTribe]:
    genOptions = os.getenv("CUSTOM_SETUP", 0)
    prompt = f"""
    Given the following world description, create {"3 distinct tribes" if genOptions else "1 tribe"} that could inhabit it.
    
    World Description:
    {world.view()}
    """
    results = await _agent.run(prompt)
    return results.output
        