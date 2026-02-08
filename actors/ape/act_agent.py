from pydantic_ai import Agent, RunContext
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
async def message(ctx: RunContext, receiver: str, message: str):
    """
    Send a message to another ape.
    """
    from actors.ape import instances
    # print(f"{ctx.deps.name} is sending a message to {receiver}")
    if receiver not in instances:
        return f"Receiver {receiver} not found"
    ctx.deps.log.append(f"[I told {receiver}]: {message}")
    for listener in instances[ctx.deps.name].listeners:
        listener(f"[I told {receiver}]: {message}")
    instances[receiver].message(ctx.deps.name, message)
    return f"Message sent"

@_act_agent.tool()
async def change_role(ctx: RunContext, new_role: str):
    """
    Change role if authority allows.
    """
    # print(f"{ctx.deps.name} is changing role to {new_role}")
    ctx.deps.role = new_role
    return f"Role changed to {new_role}"

@_act_agent.tool()
async def add_fact(ctx: RunContext, fact: str):
    """
    Add a fact to the current ape.
    """
    # print(f"{ctx.deps.name} is adding fact: {fact}")
    ctx.deps.facts.append(fact)
    return f"Fact added: {fact}"

@_act_agent.tool()
async def add_opinion(ctx: RunContext, opinion: str):
    """
    Add an opinion to the current ape.
    """
    # print(f"{ctx.deps.name} is adding opinion: {opinion}")
    ctx.deps.opinions.append(opinion)
    return f"Opinion added: {opinion}"

@_act_agent.tool()
async def edit_fact(ctx: RunContext, fact: str, new_fact: str):
    """
    Edit a fact in the current ape.
    """
    # print(f"{ctx.deps.name} is editing fact: {fact} -> {new_fact}")
    try:
        ctx.deps.facts[ctx.deps.facts.index(fact)] = new_fact
    except ValueError:
        # Fact not exactly found, try to find a close match or fail gracefully
        return f"Fact '{fact}' not found in your list. Please check your Facts list and try again."
    return f"Fact edited: {new_fact}"

@_act_agent.tool()
async def edit_opinion(ctx: RunContext, opinion: str, new_opinion: str):
    """
    Edit an opinion in the current ape.
    """
    # print(f"{ctx.deps.name} is editing opinion: {opinion} -> {new_opinion}")
    try:
        ctx.deps.opinions[ctx.deps.opinions.index(opinion)] = new_opinion
    except ValueError:
        return f"Opinion '{opinion}' not found in your list. Please check your Opinions list and try again."
    return f"Opinion edited: {new_opinion}"

async def act(ape: Ape):
    await _act_agent.run(deps=ape, user_prompt=f"""
    World Description:
    {world.instance.view()}

    Tribe Description:
    {tribe.instance.view()}

    Ape Description:
    {ape.view()}
    """)