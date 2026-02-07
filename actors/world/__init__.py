from .agent import create_worlds
from .models import CreateWorld
from interface import InterfaceType
from pydantic_world import Entity
from typing import Callable
from .view import view

instance = None

class World(CreateWorld, Entity):
    @staticmethod
    async def generate(selector: Callable[[list[InterfaceType]], int]) -> World:
        global instance
        assert instance is None, "World already generated"
        worlds = await create_worlds()
        worlds = [World(**w.model_dump()) for w in worlds]
        if len(worlds) == 1:
            instance = worlds[0]
        else:
            instance = worlds[selector([w.view() for w in worlds])]
        return instance
    
    def view(self) -> str:
        return view(self)