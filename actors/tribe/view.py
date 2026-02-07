from .models import CreateTribe

def view(tribe: CreateTribe) -> str:
    return f"""Name: {tribe.name}
Territory: {tribe.territory}
Background: {tribe.background}
Culture: {tribe.culture}
Survival Strategy: {tribe.survival_strategy}
Challenges: {', '.join(tribe.challenges)}
Relations: {tribe.tribe_relations}
"""
