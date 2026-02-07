from __future__ import annotations
from typing import TYPE_CHECKING
from .models import CreateTerritory

if TYPE_CHECKING:
    from . import World

def view(world: World):
    return f"""Description:
{world.description}

Territories:
{'\n\n'.join([territory_view(t) for t in world.territories])}
"""

def territory_view(territory: CreateTerritory):
    value = f"{territory.name}\n{territory.description}\nResources: {', '.join(territory.resources)}"
    return value