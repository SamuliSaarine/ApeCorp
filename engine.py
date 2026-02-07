from actors.world import World
from actors.tribe import Tribe
from actors.ape import Ape
from actors.player import Player
from actors import player, ape
import interface
import asyncio
import random

async def get_input(prompt):
    """Non-blocking wrapper for input."""
    return await asyncio.get_event_loop().run_in_executor(None, input, prompt)

async def print_mode(player, exit_event):
    """
    Subscribes to messages and waits for the exit_event to be set.
    """

    def callback(msg):
        print(f"\r{msg}\n> ", end="")
    # Subscribe and define what to do with messages
    player.instance.subscribe(callback)
    
    print("--- Entered PRINT MODE (Press Enter to stop) ---")
    
    # We wait here without blocking the rest of the program
    await exit_event.wait() 
    
    # Cleanup subscription so it doesn't print during Whisper Mode
    player.instance.unsubscribe(callback)

async def start():
    print("Starting simulation...")
    await World.generate(interface.ask_user_choice)
    print("World generated.")
    await Tribe.generate(interface.ask_user_choice)
    print("Tribe generated.")
    await Ape.generate()
    player.instance = ape.instances[
        interface.ask_user_choice([
            a.view() for a in ape.instances
        ])
    ]
    
    print(f"{len(ape.instances)} Apes generated.")
    player.instance = Player(random.choice(list(ape.instances.values())))
    print(f"Player is {player.instance.ape.name}")
    pause = True
    while player.instance:
        if pause:
            exit_signal = asyncio.Event()
            
            # Start the input waiter in the background
            input_task = asyncio.create_task(get_input(""))
            
            print_task = asyncio.create_task(print_mode(player, exit_signal))
            
            # Run the listener until the input_task completes
            done, pending = await asyncio.wait(
                [input_task, print_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Tell the listener to stop and clean up
            exit_signal.set()
        else:
            msg = await get_input("Whisper: ")
            player.instance.message(msg)
            
        pause = not pause
    