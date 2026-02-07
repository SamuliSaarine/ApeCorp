from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Ape

def view(ape: Ape):
    return f"""Name: {ape.name}
Age: {ape.age}
Gender: {ape.gender}
Role: {ape.role}
Facts: {', '.join(ape.facts)}
Opinions: {', '.join(ape.opinions)}
Personality: {ape.personality}"""
