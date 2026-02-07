from . import World
from .models import Territory

def view(world: World):
    return f"""Description:
{world.description}

Territories:
{'\n\n'.join([territory_view(t) for t in world.territories])}
"""

def territory_view(territory: Territory):
    value = f"{territory.name}\n{territory.description}\nResources: {', '.join(territory.resources)}"
    return value