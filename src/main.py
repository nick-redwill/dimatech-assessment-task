import asyncio

from db import create_tables, engine


async def main():
    await create_tables(engine)


asyncio.run(main())
