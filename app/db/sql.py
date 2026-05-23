from app.db.connection import db


async def fetch_one(query: str, *args):
    async with db.pool.acquire() as connection:
        return await connection.fetchrow(query, *args)


async def fetch_all(query: str, *args):
    async with db.pool.acquire() as connection:
        return await connection.fetch(query, *args)


async def execute(query: str, *args):
    async with db.pool.acquire() as connection:
        return await connection.execute(query, *args)