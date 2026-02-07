from .agent import create_tribes
from .models import CreateTribe
from interface import InterfaceType
from pydantic_world import Entity
from typing import Callable
from .view import view

instance = None

class Tribe(CreateTribe, Entity):
    @staticmethod
    async def generate(selector: Callable[[list[InterfaceType]], int]) -> 'Tribe':
        global instance
        # if instance is not None:
        #     return instance
        
        tribes = await create_tribes()
        tribes = [Tribe(**t.model_dump()) for t in tribes]
        if len(tribes) == 1:
            instance = tribes[0]
        else:
            instance = tribes[selector([t.view() for t in tribes])]
        return instance
    
    def view(self) -> str:
        return view(self)
