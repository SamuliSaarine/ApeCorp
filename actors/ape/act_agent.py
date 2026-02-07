from pydantic_ai import Agent, RunContext
from .models import CreateApe, Personality
from pydantic_world import load_md, get_model
from actors import world, tribe
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import instances
    from . import Ape

_system_prompt = load_md("actors/ape/act_prompt.md")

_act_agent = Agent(
    model=get_model("action"),
    output_type=str,
    system_prompt=_system_prompt
)

@_act_agent.tool()
def message(ctx: RunContext, receiver: str, message: str):
    """
    Send a message to another ape.
    """
    from actors.ape import instances
    print(f"{ctx.deps.name} is sending a message to {receiver}: {message}")
    if receiver not in instances:
        return f"Receiver {receiver} not found"
    ctx.deps.log.append(f"[I told {receiver}]: {message}")
    for listener in instances[receiver].listeners:
        listener(f"[I told {receiver}]: {message}")
    instances[receiver].message(ctx.deps.name, message)
    return f"Message sent"

@_act_agent.tool()
def change_role(ctx: RunContext, new_role: str):
    """
    Change role if authority allows.
    """
    ctx.deps.role = new_role
    return f"Role changed to {new_role}"

@_act_agent.tool()
def add_fact(ctx: RunContext, fact: str):
    """
    Add a fact to the current ape.
    """
    ctx.deps.facts.append(fact)
    return f"Fact added: {fact}"

@_act_agent.tool()
def add_opinion(ctx: RunContext, opinion: str):
    """
    Add an opinion to the current ape.
    """
    ctx.deps.opinions.append(opinion)
    return f"Opinion added: {opinion}"

@_act_agent.tool()
def edit_fact(ctx: RunContext, fact: str, new_fact: str):
    """
    Edit a fact in the current ape.
    """
    ctx.deps.facts[ctx.deps.facts.index(fact)] = new_fact
    return f"Fact edited: {new_fact}"

@_act_agent.tool()
def edit_opinion(ctx: RunContext, opinion: str, new_opinion: str):
    """
    Edit an opinion in the current ape.
    """
    ctx.deps.opinions[ctx.deps.opinions.index(opinion)] = new_opinion
    return f"Opinion edited: {new_opinion}"

@_act_agent.tool()
def edit_relationship(ctx: RunContext, ape: str, new_relationship: str):
    """
    Edit a relationship in the current ape.
    """
    ctx.deps.relationships[ape] = new_relationship
    return f"Relationship edited: {new_relationship}"

async def act(ape: Ape):
    await _act_agent.run(deps=ape, user_prompt=f"""
    World Description:
    {world.instance.view()}

    Tribe Description:
    {tribe.instance.view()}

    Ape Description:
    {ape.view()}
    """)