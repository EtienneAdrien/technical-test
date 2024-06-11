from functools import lru_cache

import arq
from arq import create_pool
from arq.connections import RedisSettings, ArqRedis

from app import config
from app.features.user_code.jobs import handle_post_user_creation_job
from app.utils.db.connect import connection_pool


def redis_settings():
    return RedisSettings(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        database=config.REDIS_DB,
        password=config.REDIS_PASSWORD,
    )


REDIS_SETTINGS = redis_settings


class RedisPool:
    def __init__(self):
        self.redis_pool: ArqRedis | None = None

    async def startup(self):
        self.redis_pool = await create_pool(REDIS_SETTINGS())
        return self

    async def get_redis(self):
        return self.redis_pool


@lru_cache(maxsize=1)
def redis_pool():
    return RedisPool()


async def get_redis() -> ArqRedis:
    yield await redis_pool().get_redis()


async def on_startup(ctx: dict) -> dict:
    """
    Pass the db connection to the context, so it can be used in the worker easily
    Args:
        ctx: The context for the worker

    Returns:
        The context
    """
    await connection_pool().open()
    ctx["db"] = await connection_pool().getconn()

    return ctx


async def on_shutdown(ctx: dict) -> dict:
    """
    Closes the db connection.
    Args:
        ctx: The context for the worker

    Returns:
        The context
    """
    await connection_pool().close()
    await connection_pool().putconn(ctx["db"])

    return ctx


class WorkerSettings(arq.Worker):
    functions = [handle_post_user_creation_job]
    redis_settings = REDIS_SETTINGS()
    on_startup = on_startup
    on_shutdown = on_shutdown
