from actors.world import World
from actors.tribe import Tribe
from actors.ape import Ape
from actors import player, ape
import interface

async def start():
    await World.generate(interface.ask_user_choice)
    await Tribe.generate(interface.ask_user_choice)
    await Ape.generate()
    player.instance = ape.instances[
        interface.ask_user_choice([
            a.view() for a in ape.instances
            ]
        )
    ]
    
    