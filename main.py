from dotenv import load_dotenv
# IMPORTANT: Load .env file before importing anything else
load_dotenv()

import engine
import asyncio

async def main():
    try:
        await engine.start()
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nSimulation stopping...")
    finally:
        # Cancel all running tasks
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        
        # Wait for all tasks to be cancelled
        if tasks:
            # We don't want to see "Task was destroyed but it is pending!" either
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except (RuntimeError, asyncio.CancelledError):
                pass
        print("Simulation stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass # Handle case where interrupt happens during loop setup/teardown