from .agent import create_tribes
from .models import CreateTribe
from interface import InterfaceType
from pydantic_world import Entity
from typing import Callable
from .view import view
from ..world import World

instance = None

class Tribe(CreateTribe, Entity):
    def __init__(self, tribe: CreateTribe):
        self.name = tribe.name
        self.territory = tribe.territory
        self.background = tribe.background
        self.culture = tribe.culture
        self.survival_strategy = tribe.survival_strategy
        self.challenges = tribe.challenges
        self.tribe_relations = tribe.tribe_relations

    @staticmethod
    async def generate(world: World, selector: Callable[[list[InterfaceType]], int]) -> 'Tribe':
        global instance
        # if instance is not None:
        #     return instance
        
        tribes = await create_tribes(world)
        if len(tribes) == 1:
            instance = Tribe(tribes[0])
        else:
            instance = Tribe(tribes[selector([t.view() for t in tribes])])
        return instance
    
    def view(self) -> str:
        return view(self)
