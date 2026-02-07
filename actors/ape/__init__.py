from __future__ import annotations

from .agent import create_apes
from . import spawn_agent, act_agent
from .models import CreateApe, Personality
from pydantic_world import Entity
from actors import world, tribe
import random
from .view import view as _view
from typing import Callable, Set
import asyncio

instances: dict[str, Ape] = {}

class Ape(CreateApe, Entity):
    personality: Personality
    log: list[str] = []
    listeners: Set[Callable[[str], None]] = set()
    acting: bool = False
    messages_while_acting: bool = False

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
        
        created_apes = await spawn_agent.create_apes(personalities)
        
        new_apes = {}
        for i, ape_data in enumerate(created_apes):
            new_ape = Ape(**ape_data.model_dump(), personality=personalities[i])
            new_apes[new_ape.name] = new_ape
            
        instances = new_apes
        for ape in instances.values():
            asyncio.create_task(ape.act())
        return instances

    def view(self) -> str:
        return _view(self)

    def subscribe(self, callback: Callable[[str], None]):
        self.listeners.add(callback)

    def unsubscribe(self, callback: Callable[[str], None]):
        self.listeners.remove(callback)

    def message(self, sender: str, message: str):
        if sender == "MYSELF":
            self.log.append(f"[I thought]: {message}")
        else:
            self.log.append(f"[{sender} said]: {message}")
            for listener in self.listeners:
                listener(f"[{sender}]: {message}")
        if self.acting:
            self.messages_while_acting = True
        else:
            asyncio.create_task(self.act())

    async def act(self):
        if self.acting:
            return
        print(f"{self.name} is acting.")
        self.messages_while_acting = False
        self.acting = True
        await act_agent.act(self)
        self.acting = False
        if self.messages_while_acting:
            asyncio.create_task(self.act())
        else:
            await asyncio.sleep(random.randint(2, 10))
            asyncio.create_task(self.act())
