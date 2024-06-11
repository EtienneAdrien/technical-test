from _pytest.monkeypatch import MonkeyPatch
from arq import ArqRedis
from psycopg_pool.abc import ACT

from app import config
from app.tests.models import *
from app.utils.db.connect import (
    get_db_acm,
    connection_pool,
)
from app.utils.db.init import delete_database, init_database_schema
from app.utils.redis.connect import redis_pool


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    We use this form of the fixture to set the `asyncio` backend for the entire session, whereas
    using @pytest.mark.anyio would not give the correct scope and would close the event loop before the session ends.
    """
    return "asyncio"


@pytest.fixture(scope="session")
def monkeypatch_session() -> MonkeyPatch:
    """
    We redefine the monkeypatch fixture to have the correct scope, otherwise it would be scoped as "function" and
    couldn't be used alongside the db initialisation.
    Returns:
        MonkeyPatch: The monkeypatch fixture
    """
    m = MonkeyPatch()
    yield m
    m.undo()


@pytest.fixture(scope="session")
async def init_db(monkeypatch_session, anyio_backend) -> None:
    """
    Monkeypatch the db settings to point to a test database, initialise the database and open the connection pool.
    After the test session, close the connection pool and delete the test database.
    """
    monkeypatch_session.setattr(config, "POSTGRES_DB", "test-db")

    await init_database_schema()
    await connection_pool().open()

    try:
        yield

    finally:
        await connection_pool().close()
        await delete_database()


async def truncate(conn):
    """
    Truncate the database.
    Not the best solution, but since we only have two tables, this is more than enough.
    """
    await conn.rollback()
    tables = ["user_code", "user_data"]
    await conn.execute(f"TRUNCATE TABLE {', '.join(tables)} CASCADE;")
    await conn.commit()


@pytest.fixture(scope="function")
async def db(init_db) -> ACT:
    """
    Fixture to get the actual db connection, truncate the tables at the end of each test, this is faster than recreating
    it every time.
    """
    async with get_db_acm() as db:
        try:
            yield db
        finally:
            await truncate(conn=db)


@pytest.fixture(scope="session")
async def redis(monkeypatch_session) -> ArqRedis:
    """
    Create a redis pool and a redis client, we use a test database (15).
    """
    monkeypatch_session.setattr(config, "REDIS_DB", 15)

    pool = await redis_pool().startup()
    redis = await pool.get_redis()

    yield redis

    await redis.flushall()
