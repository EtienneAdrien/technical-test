import pytest

from app.features.user.exceptions import UserNotFoundError
from app.features.user_code import crud, exceptions


async def test_create_user_code(anyio_backend, db, create_user):
    user_id = await create_user(email="test", password="test")
    user_code = await crud.create_user_code(conn=db, user_id=user_id)

    # Have to commit there sadly since it's not done in the function, so it can be used in a transaction elsewhere
    await db.commit()

    assert len(user_code) == 4 and user_code.isdigit()


async def test_create_user_code_no_user_found(anyio_backend, db):
    with pytest.raises(UserNotFoundError):
        await crud.create_user_code(conn=db, user_id=9999)


async def test_start_activation(anyio_backend, db, create_user, create_user_code):
    async def get_code():
        await cursor.execute(
            "SELECT date_start_validity FROM user_code WHERE user_id = %s AND code = %s",
            (user_id, user_code),
        )
        return await cursor.fetchone()

    user_id = await create_user(email="test", password="test")
    user_code = await create_user_code(user_id=user_id)

    async with db.cursor() as cursor:
        result = await get_code()
        assert result[0] is None

        await crud.start_activation(conn=db, user_id=user_id, user_code=user_code)
        result = await get_code()
        assert result[0] is not None


async def test_start_activation_no_user_code_found(anyio_backend, db, create_user):
    user_id = await create_user(email="test", password="test")

    with pytest.raises(exceptions.UserCodeNotFoundError):
        await crud.start_activation(conn=db, user_id=user_id, user_code="whatever")


async def test_get_user_code(anyio_backend, db, create_user, create_user_code):
    user_id = await create_user(email="test", password="test")
    user_code = await create_user_code(user_id=user_id, code="1234")

    user_code_obj = await crud.get_user_code(
        conn=db, user_email="test", user_code="1234"
    )

    assert user_code_obj.user_id == user_id
    assert user_code_obj.code == user_code


async def test_get_user_code_no_user_code_found(anyio_backend, db, create_user):
    await create_user(email="test", password="test")
    with pytest.raises(exceptions.UserCodeNotFoundError):
        await crud.get_user_code(conn=db, user_email="test", user_code="1234")


async def test_get_user_code_no_user_found(anyio_backend, db, create_user):
    with pytest.raises(exceptions.UserCodeNotFoundError):
        await crud.get_user_code(conn=db, user_email="test", user_code="1234")
