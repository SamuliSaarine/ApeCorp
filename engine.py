from actors import {
    tribe, 
}
import interface

async def start():
    await World.generate(interface.ask_user_choice)
    await Tribe.generate(interface.ask_user_choice)
    await Ape.generate(interface.ask_user_choice)
    
    