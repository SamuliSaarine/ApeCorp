def world_view(world):
    return f"""Description:
{world.description}

Territories:
{'\n\n'.join(map(territory_view, world.territories))}
"""

def territory_view(territory):
    value = f"{territory.name}\n{territory.description}\nResources: {', '.join(territory.resources)}"
    return value