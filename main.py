from dotenv import load_dotenv
# IMPORTANT: Load .env file before importing anything else
load_dotenv()

import engine
import asyncio

async def main():
    await engine.start()

if __name__ == "__main__":
    asyncio.run(main())