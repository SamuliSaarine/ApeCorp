from .agent import create_worlds
from .models import CreateWorld
from interface import InterfaceType
from pydantic_world import Entity
from typing import Callable
from .view import view

instance = None

class World(CreateWorld, Entity):
    def __init__(self, world: CreateWorld):
        self.description = world.description
        self.territories = world.territories

    @staticmethod
    async def generate(selector: Callable[[list[InterfaceType]], int]) -> World:
        global instance
        assert instance is None, "World already generated"
        worlds = await create_worlds()
        if len(worlds) == 1:
            instance = World(worlds[0])
        else:
            instance = World(worlds[selector([w.view() for w in worlds])])
        return instance
    
    def view(self) -> str:
        return view(self)