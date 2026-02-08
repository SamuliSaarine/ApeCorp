from pydantic_ai import Agent
from .models import ApeSocialInfo, Personality, SocialBlueprint, ApeDetails
from pydantic_world import load_md, get_model
from actors import world, tribe
import asyncio

_blueprint_prompt = load_md("actors/ape/spawn_blueprint_prompt.md")
_details_prompt = load_md("actors/ape/spawn_details_prompt.md")

_blueprint_agent = Agent(
    model=get_model("creative"),
    output_type=SocialBlueprint,  # Expects list of ApeSocialInfo, list of Relationship
    system_prompt=_blueprint_prompt
)

_details_agent = Agent(
    model=get_model("creative"),
    output_type=ApeDetails,
    system_prompt=_details_prompt
)

async def create_apes(personalities: list[Personality]) -> list[tuple[ApeSocialInfo, ApeDetails]]:
    if world.instance is None or tribe.instance is None:
        raise ValueError("World and Tribe must be generated before creating Apes.")

    count = len(personalities)
    # print(f"Generating Social Blueprint for {count} apes...")

    # 1. Generate Social Blueprint (Roles, Names, Relationships)
    personality_specs = []
    for i, p in enumerate(personalities):
        spec = (
            f"APE #{i+1}\n"
            f"- Openness: {p.openness}/100\n"
            f"- Conscientiousness: {p.conscientiousness}/100\n"
            f"- Extraversion: {p.extraversion}/100\n"
            f"- Agreeableness: {p.agreeableness}/100\n"
            f"- Neuroticism: {p.neuroticism}/100"
        )
        personality_specs.append(spec)

    personality_block = "\n\n".join(personality_specs)

    blueprint_prompt = f"""
        ### CONTEXT
        World: {world.instance.view()}
        Tribe: {tribe.instance.view()}

        ### MANDATORY TASK
        You must generate a Social Blueprint for EXACTLY {count} Apes.
        The order of apes in your 'apes' list MUST correspond to the personality profiles below.

        ### PERSONALITY PROFILES
        {personality_block}
        """

    blueprint_result = await _blueprint_agent.run(blueprint_prompt)
    blueprint: SocialBlueprint = blueprint_result.output

    # print(blueprint.model_dump_json(indent=2))

    if len(blueprint.apes) != count:
        raise ValueError(f"Blueprint returned {len(blueprint.apes)} apes, expected {count}.")

    # print("Social Blueprint generated. Generating details for each ape in parallel...")

    # 2. Generate Details (Facts, Opinions) for each ape in parallel
    async def generate_details(social_info: ApeSocialInfo, personality: Personality) -> tuple[ApeSocialInfo, ApeDetails]:
        # Filter relationships relevant to this ape
        my_relationships = [
            r for r in blueprint.relationships 
            if r.ape1 == social_info.name or r.ape2 == social_info.name
        ]
        
        details_prompt = f"""
            ### CONTEXT
            World: {world.instance.view()}
            Tribe: {tribe.instance.view()}
            
            ### SOCIAL BLUEPRINT
            All Apes: {[a.model_dump() for a in blueprint.apes]}
            All Relationships: {[r.model_dump() for r in blueprint.relationships]}

            ### THIS APE
            Name: {social_info.name}
            Age: {social_info.age}
            Gender: {social_info.gender}
            Role: {social_info.role}
            
            Personality: {personality.model_dump()}
            
            Relationships involving {social_info.name}:
            {[r.model_dump() for r in my_relationships]}
            """
            
        details_result = await _details_agent.run(details_prompt)
        return (social_info, details_result.output)

    tasks = []
    for i, ape_social in enumerate(blueprint.apes):
        tasks.append(generate_details(ape_social, personalities[i]))

    created_apes = await asyncio.gather(*tasks)

    return created_apes