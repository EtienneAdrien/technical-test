import datetime

import httpx
from httpx import AsyncClient

from app import config
from app.main import app
from app.utils.redis.connect import redis_pool


async def test_create_user(anyio_backend, db, redis):
    async with AsyncClient(app=app, base_url="http://test/user") as ac:
        response = await ac.post("/", json={"email": "test", "password": "test"})
        assert response.status_code == 200

    async with db.cursor() as cursor:
        await cursor.execute(
            "SELECT user_data.email, user_data.activated, user_code.code "
            "FROM user_data "
            "JOIN user_code on user_data.user_id = user_code.user_id "
            "WHERE email = 'test'"
        )
        result = await cursor.fetchone()

        assert result[0] == "test"
        assert result[1] == 0

    redis = await redis_pool().get_redis()
    jobs = await redis.queued_jobs(queue_name=config.QUEUE_NAME)

    assert len(jobs) == 1
    assert jobs[0].kwargs["email"] == "test"
    assert jobs[0].kwargs["user_code"] == result[2]


async def test_validate_user(anyio_backend, db, redis, create_user, create_user_code):
    user_id = await create_user(email="test", password="test", activated=False)
    code = await create_user_code(
        user_id=user_id, date_start_validity=datetime.datetime.now(datetime.UTC)
    )

    auth = httpx.BasicAuth(username="test", password="test")

    async with AsyncClient(app=app, base_url="http://test/user") as ac:
        response = await ac.get("/validate", auth=auth, params={"user_code": code})
        assert response.status_code == 200

    async with db.cursor() as cursor:
        await cursor.execute(
            "SELECT user_data.activated "
            "FROM user_data "
            "WHERE user_data.user_id = %s",
            (user_id,),
        )

        result = await cursor.fetchone()

        assert result[0] == 1


async def test_test_user_connection(
    anyio_backend, db, redis, create_user, create_user_code
):
    user_id = await create_user(email="test", password="test", activated=True)
    await create_user_code(
        user_id=user_id, date_start_validity=datetime.datetime.now(datetime.UTC)
    )

    auth = httpx.BasicAuth(username="test", password="test")

    async with AsyncClient(app=app, base_url="http://test/user") as ac:
        response = await ac.get("/", auth=auth)
        assert response.status_code == 200
