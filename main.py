from dotenv import load_dotenv
# IMPORTANT: Load .env file before importing anything else
load_dotenv()

import asyncio
from ui import run_ui

async def main():
    await run_ui()

if __name__ == "__main__":
    asyncio.run(main())