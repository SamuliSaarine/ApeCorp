from .agent import create_apes
from .models import CreateApe, Personality
from pydantic_world import Entity
from actors import world, tribe
import random
from .view import view as _view

instances: list[Ape] = []

class Ape(CreateApe, Entity):
    personality: Personality
    
    @staticmethod
    async def generate() -> list[Ape]:
        global instances
        
        if world.instance is None:
            raise ValueError("World instance is not generated yet.")
        if tribe.instance is None:
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
            new_ape = Ape(**ape_data.model_dump(), personality=personalities[i])
            new_apes.append(new_ape)
            
        instances = new_apes
        return instances

    def view(self) -> str:
        return _view(self)