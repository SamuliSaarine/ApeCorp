from utils.get_model import get_model
from pydantic_ai import Agent
from .models import CreateApe, Personality
import actors.world
import actors.tribe
from pydantic_world import load_md

_system_prompt = load_md("actors/ape/system_prompt.md")

agent = Agent(
    model=get_model("creative"),
    output_type=CreateApe,
    system_prompt=_system_prompt
)

async def create_apes(personalities: list[Personality]) -> list[CreateApe]:
    world = actors.world.instance
    tribe = actors.tribe.instance
    
    if world is None or tribe is None:
        raise ValueError("World and Tribe must be generated before creating Apes.")

    apes = []
    for personality in personalities:
        prompt = f"""
        World Description:
        {world.view()}

        Tribe Description:
        {tribe.view()}

        Target Personality:
        Openness: {personality.openness}/100
        Conscientiousness: {personality.conscientiousness}/100
        Extraversion: {personality.extraversion}/100
        Agreeableness: {personality.agreeableness}/100
        Neuroticism: {personality.neuroticism}/100
        """
        result = await agent.run(prompt)
        apes.append(result.data)
    
    return apes