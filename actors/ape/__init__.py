from . import spawn_agent, act_agent
from .models import ApeSocialInfo, ApeDetails, Personality
from pydantic_world import Entity
from actors import world, tribe
import random
from .view import view as _view
from typing import Callable, Set
import asyncio

instances: dict[str, Ape] = {}

class Ape(ApeSocialInfo, ApeDetails, Entity):
    personality: Personality
    log: list[str] = []
    listeners: Set[Callable[[str], None]] = set()
    acting: bool = False

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
        
        created_data = await spawn_agent.create_apes(personalities)
        
        new_apes = {}
        for i, (social, details) in enumerate(created_data):
            new_ape = Ape(
                **social.model_dump(),
                **details.model_dump(),
                personality=personalities[i],
            )
            asyncio.create_task(new_ape.act())
            new_apes[new_ape.name] = new_ape
            
        instances = new_apes
        return instances

    def view(self) -> str:
        return _view(self)

    def info_view(self):
        from .ui_view import ui_view as ape_ui_view
        from actors.world.ui_view import ui_view as world_ui_view
        from actors.tribe.ui_view import ui_view as tribe_ui_view
        from fasthtml.common import Div
        
        # We return a FastHTML component structure directly
        w_view = world_ui_view(world.instance) if world.instance else Div("Unknown World")
        t_view = tribe_ui_view(tribe.instance) if tribe.instance else Div("Unknown Tribe")
        a_view = ape_ui_view(self)
        
        return Div(
            w_view,
            t_view,
            a_view,
            cls="space-y-4"
        )


    def subscribe(self, callback: Callable[[str], None]):
        self.listeners.add(callback)

    def unsubscribe(self, callback: Callable[[str], None]):
        self.listeners.remove(callback)

    _act_task: asyncio.Task | None = None
    last_activity: float = 0
    status: str = "resting"  # "busy", "pacing", "resting"

    def message(self, sender: str, message: str):
        if sender == "MYSELF":
            self.log.append(f"[I thought]: {message}")
            for listener in self.listeners:
                listener(f"[I thought]: {message}")
        else:
            self.log.append(f"[{sender} said]: {message}")
            for listener in self.listeners:
                listener(f"[{sender}]: {message}")
        
        # Update activity timestamp on incoming message
        import time
        self.last_activity = time.time()

        if self.status == "busy":
            # Already acting, do nothing special
            pass
        elif self.status == "resting" and self._act_task:
            # Wake up immediately if resting (long sleep)
            self._act_task.cancel()
        elif self._act_task is None or self._act_task.done():
            # Not running, start it
            self._act_task = asyncio.create_task(self.act())

    async def act(self):
        # Guard against nested calls if called manually
        if self.status == "busy":
            return

        self.status = "busy"
        # print(f"{self.name} is acting.")
        
        try:
            try:
                await act_agent.act(self)
            except Exception as e:
                if "Executor shutdown" in str(e) or "generator" in str(e):
                    pass # Expected during shutdown
                else:
                    pass # print(f"Error acting for {self.name}: {e}")
            
            # Scheduling next action
            import time
            now = time.time()
            # If we had activity recently (e.g. within 60 seconds), we sleep for a short time (pacing)
            # Otherwise we sleep for a long time (resting)
            if now - self.last_activity < 60:
                sleep_time = random.randint(2, 5)
                self.status = "pacing"
            else:
                sleep_time = random.randint(5, 20)
                self.status = "resting"

            # print(f"{self.name} is {self.status} for {sleep_time} seconds.")
            
            try:
                await asyncio.sleep(sleep_time)
            except asyncio.CancelledError:
                # print(f"{self.name} woke up from sleep context!")
                pass    
        
        except Exception as e:
            if "Executor shutdown" in str(e) or "generator" in str(e):
                pass
            else:
                pass # print(f"Critical error in act loop for {self.name}: {e}")
        except asyncio.CancelledError:
            pass
            
        finally:
            # We must ensure status is not 'busy' before restarting, 
            # otherwise the next loop will return immediately.
            if self.status == "busy":
                self.status = "resting"
                
            # Loop
            # Catch possible shutdown error
            try:
                self._act_task = asyncio.create_task(self.act())
            except RuntimeError:
                pass # Event loop closed
