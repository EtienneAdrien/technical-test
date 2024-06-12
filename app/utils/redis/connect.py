from functools import lru_cache

from arq import create_pool
from arq.connections import RedisSettings, ArqRedis

from app import config


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
