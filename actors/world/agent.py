from pydantic_world import get_model, load_md
from pydantic_ai import Agent
from .models import CreateWorld
import os

system_prompt = load_md("actors/world/system_prompt.md")

_creator = Agent(
    model=get_model("creative"),
    system_prompt=system_prompt,
    output_type=list[CreateWorld]
)

async def create_worlds() -> list[CreateWorld]:
    genOptions = int(os.getenv("CUSTOM_SETUP", 0))
    prompt = f"""
    Generate {3 if genOptions else 1} world option{'s' if genOptions else ''}.
    """
    results = await _creator.run(prompt)
    return results.output