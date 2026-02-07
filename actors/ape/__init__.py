from .agent import create_apes
from .models import CreateApe, Personality
from pydantic_world import Entity
import actors.world
import actors.tribe
import random

instances: list['Ape'] = []

class Ape(CreateApe, Entity):
    def __init__(self, ape: CreateApe, personality: Personality):
        self.name = ape.name
        self.age = ape.age
        self.gender = ape.gender
        self.role = ape.role
        self.facts = ape.facts
        self.opinions = ape.opinions
        self.personality = personality

    @staticmethod
    async def generate() -> list['Ape']:
        global instances
        
        world = actors.world.instance
        tribe = actors.tribe.instance
        
        if world is None:
            raise ValueError("World instance is not generated yet.")
        if tribe is None:
            raise ValueError("Tribe instance is not generated yet.")

        personalities = []
        for _ in range(4):
            personalities.append(Personality(
                openness=random.randint(0, 100),
                conscientiousness=random.randint(0, 100),
                extraversion=random.randint(0, 100),
                agreeableness=random.randint(0, 100),
                neuroticism=random.randint(0, 100)
            ))
        
        created_apes = await create_apes(personalities)
        
        new_apes = []
        for i, ape_data in enumerate(created_apes):
            new_ape = Ape(ape_data, personalities[i])
            new_apes.append(new_ape)
            
        instances = new_apes
        return instances
