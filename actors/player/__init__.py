from pydantic_world import Entity
from typing import Callable
from actors.ape import Ape

instance = None

class Player():
    ape: Ape
    
    def __init__(self, ape: Ape):
        global instance
        assert instance is None, "Player already generated"
        instance = self
        self.ape = ape

    def subscribe(self, callback: Callable[[str], None]):
        return self.ape.subscribe(callback)

    def unsubscribe(self, callback: Callable[[str], None]):  
        self.ape.unsubscribe(callback)

    def message(self, message: str):
        self.ape.message("MYSELF", message)