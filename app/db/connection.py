import asyncpg
from app.core.config import settings


class Database:
    pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            statement_cache_size=0
        )

    async def disconnect(self):
        await self.pool.close()


db = Database()