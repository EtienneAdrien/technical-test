import pytest

from app.features.user import crud, schemas, exceptions
from app.utils import security


async def test_create_user_with_code(anyio_backend, db):
    user_id, user_code = await crud.create_user_with_code(
        conn=db, user=schemas.UserIn(email="test", password="test")
    )

    async with db.cursor() as cursor:
        await cursor.execute(
            "SELECT user_id, password, email, activated "
            "FROM user_data "
            "WHERE user_id = %s",
            (user_id,),
        )

        user_data = await cursor.fetchone()

        assert security.check_hash(password="test", hash_=user_data[1])
        assert user_data[2] == "test"
        assert user_data[3] is False

        await cursor.execute(
            "SELECT code, date_start_validity FROM user_code WHERE user_id = %s",
            (user_id,),
        )

        user_code_obj = await cursor.fetchone()

        assert user_code_obj[0] == user_code
        assert not user_code_obj[1]


async def test_create_user_with_code_user_already_exists(
    anyio_backend, db, create_user
):
    await create_user(email="test", password="test")

    with pytest.raises(exceptions.UserAlreadyExistsError):
        await crud.create_user_with_code(
            conn=db, user=schemas.UserIn(email="test", password="testtest")
        )


async def test_update_user_activation(anyio_backend, db, create_user):
    user = await create_user(email="test", password="test")

    await crud.update_user_activation(user_id=user, db=db, activated=True)

    async with db.cursor() as cursor:
        await cursor.execute(
            "SELECT activated FROM user_data WHERE user_id = %s", (user,)
        )

        user_data = await cursor.fetchone()

        assert user_data[0] is True


async def test_update_user_activation_user_not_found(anyio_backend, db):
    with pytest.raises(exceptions.UserNotFoundError):
        await crud.update_user_activation(user_id=9999, db=db, activated=True)


async def test_get_user_by_email(anyio_backend, db, create_user):
    user_id = await create_user(email="test", password="test")
    user = await crud.get_user_by_email(email="test", conn=db)

    assert user.email == "test"
    assert user.user_id == user_id


async def test_get_user_by_email_no_user_found(anyio_backend, db):
    user = await crud.get_user_by_email(email="test", conn=db)

    assert user is None
