from contextlib import asynccontextmanager
from functools import lru_cache

from psycopg_pool import AsyncConnectionPool
from psycopg_pool.abc import ACT
from typing_extensions import AsyncContextManager

from app import config


@lru_cache(maxsize=1)
def connection_pool():
    return AsyncConnectionPool(
        min_size=5,
        max_size=10,
        conninfo=f"""dbname={config.POSTGRES_DB} 
            user={config.POSTGRES_USER} 
            password={config.POSTGRES_PASSWORD} 
            host={config.POSTGRES_HOST} 
            port={config.POSTGRES_PORT}""",
        open=False,
        timeout=3,
    )


async def get_db() -> ACT:
    async with connection_pool().connection() as conn:
        yield conn


get_db_acm = asynccontextmanager(get_db)
