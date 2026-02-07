from actors.tribe import Tribe
from actors.world import World
import interface

async def start():
    await World.generate(interface.ask_user_choice)
    await Tribe.generate(interface.ask_user_choice)
    
    
    