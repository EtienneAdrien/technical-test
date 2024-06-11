import datetime

import pytest

from app.features import user_code
from app.features.user_code import exceptions


async def test_is_user_code_valid(anyio_backend, db, create_user, create_user_code):
    now = datetime.datetime.now(datetime.UTC)

    user_id = await create_user(email="test", password="test")
    code = await create_user_code(user_id=user_id, date_start_validity=now)

    user_code_obj = await user_code.services.validation._is_user_code_valid(
        user_email="test", user_code=code, conn=db
    )

    assert user_code_obj.user_id == user_id
    assert user_code_obj.code == code
    assert user_code_obj.date_start_validity == now


async def test_is_user_code_valid_no_user_code_found(
    anyio_backend, db, create_user, create_user_code
):
    await create_user(email="test", password="test")

    with pytest.raises(exceptions.UserCodeNotFoundError):
        await user_code.services.validation._is_user_code_valid(
            user_email="test", user_code="9999", conn=db
        )


async def test_is_user_code_valid_expired_code(
    anyio_backend, db, create_user, create_user_code
):
    now_minus_1 = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)

    user_id = await create_user(email="test", password="test")
    code = await create_user_code(user_id=user_id, date_start_validity=now_minus_1)

    with pytest.raises(exceptions.ExpiredUserCodeError):
        await user_code.services.validation._is_user_code_valid(
            user_email="test", user_code=code, conn=db
        )


async def test_validate_user(anyio_backend, db, create_user, create_user_code):
    now = datetime.datetime.now(datetime.UTC)

    user_id = await create_user(email="test", password="test")
    code = await create_user_code(user_id=user_id, date_start_validity=now)

    await user_code.services.validation.validate_user(
        user_email="test", user_code=code, conn=db
    )

    async with db.cursor() as cursor:
        await cursor.execute(
            "SELECT activated FROM user_data WHERE user_data.user_id = %s", (user_id,)
        )

        result = await cursor.fetchone()
        assert result[0]
