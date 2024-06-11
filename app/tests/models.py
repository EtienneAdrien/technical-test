import datetime

import pytest

from app.features.user_code import utils
from app.utils import security


@pytest.fixture
def create_user(anyio_backend, db):
    async def _create_user(
        email: str = "test", password: str = "test", activated: bool = False
    ) -> int:
        async with db.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO user_data (email, password, activated) VALUES (%s, %s, %s) RETURNING user_id",
                (email, security.hash_password(password), activated),
            )

            result = await cursor.fetchone()
            user_id = result[0]

            await db.commit()

            return user_id

    return _create_user


@pytest.fixture
def create_user_code(anyio_backend, db):
    async def _create_user_code(
        user_id: int,
        code: str = None,
        date_start_validity: datetime.datetime | None = None,
    ) -> str:
        code = code or utils.generate_code()

        async with db.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO user_code (user_id, code, date_start_validity) VALUES (%s, %s, %s) RETURNING code",
                (user_id, code, date_start_validity),
            )

            result = await cursor.fetchone()
            code = result[0]

            await db.commit()

            return code

    return _create_user_code
