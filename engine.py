from agents import map, tribe
import state
import interface
from model_views import world_view

async def start():
    worlds = await map.run()
    world_choice = interface.ask_user_choice([world_view(world) for world in worlds])
    state.world = worlds[world_choice]
    state.log.append("WORLD_CREATED")
    tribes = await tribe.run(state.world)
    state.tribes = tribes
    state.log.append("TRIBES_CREATED")
    
    