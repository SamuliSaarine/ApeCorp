from pydantic_ai import Agent
from .models import CreateApe, Personality
from pydantic_world import load_md, get_model
from actors import world, tribe

_system_prompt = load_md("actors/ape/system_prompt.md")

_act_agent = Agent(
    model=get_model("action"),
    output_type=list[CreateApe],
    system_prompt=_system_prompt
)

async def act_apes(personalities: list[Personality]) -> list[CreateApe]:
    if world.instance is None or tribe.instance is None:
        raise ValueError("World and Tribe must be generated before creating Apes.")

    prompt = f"""
        World Description:
        {world.instance.view()}

        Tribe Description:
        {tribe.instance.view()}

        Generate {len(personalities)} apes with the following personalities:
        """
    for i, p in enumerate(personalities):
        prompt += f"""
        Target Personality {i+1}:
        Openness: {p.openness}/100
        Conscientiousness: {p.conscientiousness}/100
        Extraversion: {p.extraversion}/100
        Agreeableness: {p.agreeableness}/100
        Neuroticism: {p.neuroticism}/100

        """

    result = await _create_agent.run(prompt)
    return result.output