from actors.world import World
from actors.tribe import Tribe
from actors.ape import Ape
from actors.player import Player
from actors import player, ape
import interface
import random
from fasthtml.common import Div, fast_app
import uvicorn

# FastHTML App Setup
app, rt = fast_app()

@rt('/')
def get():
    # Helper to render the full app via interface
    return interface.render_app(player.instance)

@rt('/whisper')
async def post(msg: str):
    if player.instance:
        player.instance.message(msg)
        return interface.render_log(f"You whispered: {msg}")
    return interface.render_log("Error: Player not initialized")

@rt('/log_updates')
def log_updates():
    if player.instance:
        # Get last 20 lines of log
        recent_logs = player.instance.ape.log[-20:]
        # Wrap in a fragment or Div to ensure it renders correctly as a list of elements
        return Div(*[interface.render_log(msg) for msg in recent_logs])
    return interface.render_log("Waiting for player initialization...")

# We could have a separate endpoint for polling info updates or another WS
@rt('/info/{section}')
async def info_updates(section: str):
    if player.instance:
        return interface.render_info_content(player.instance, section)
    return interface.render_info_content(None, section)

async def start():
    print("Starting simulation...")
    # Initialize the world
    await World.generate(interface.ask_user_choice)
    print("World generated.")
    await Tribe.generate(interface.ask_user_choice)
    print("Tribe generated.")
    await Ape.generate()
    print(f"{len(ape.instances)} Apes generated.")
    
    # Select player
    player.instance = Player(random.choice(list(ape.instances.values())))
    print(f"Player is {player.instance.ape.name}")
    
    print("Starting Web Server at http://0.0.0.0:5001")
    
    # Run Uvicorn Server
    config = uvicorn.Config(app, host='0.0.0.0', port=5001, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()