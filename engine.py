from agents import corp_builder
import state
import interface
from model_views import corp_view

async def start():
    corps = await corp_builder.run()
    choice = interface.ask_user_choice([corp_view(corp) for corp in corps])
    state.corporation = corps[choice]