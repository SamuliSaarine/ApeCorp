from __future__ import annotations

def view(ape: Ape):
    return f"""Name: {ape.name}
Age: {ape.age}
Gender: {ape.gender}
Role: {ape.role}
Facts: {', '.join(ape.facts)}
Opinions: {', '.join(ape.opinions)}
Personality: {ape.personality}
Relationships: {', '.join([f'{k}: {v}' for k, v in ape.relationships.items()])}
Memory: {', '.join(ape.log[-10:])}
"""
