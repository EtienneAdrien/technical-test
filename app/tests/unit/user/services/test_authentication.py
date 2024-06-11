import pytest

from app.features import user
from app.features.user import exceptions


async def test__verify_user_credentials(anyio_backend, db, create_user):
    await create_user(email="test", password="test", activated=True)

    await user.services.authentication._verify_user_credentials(
        email="test",
        password="test",
        with_activation=True,
        conn=db,
    )

    await user.services.authentication._verify_user_credentials(
        email="test",
        password="test",
        with_activation=False,
        conn=db,
    )


async def test__verify_user_credentials_not_activated(anyio_backend, db, create_user):
    await create_user(email="test", password="test", activated=False)

    with pytest.raises(exceptions.UserNotActivatedError):
        await user.services.authentication._verify_user_credentials(
            email="test",
            password="test",
            with_activation=True,
            conn=db,
        )

    await user.services.authentication._verify_user_credentials(
        email="test",
        password="test",
        with_activation=False,
        conn=db,
    )


async def test__verify_user_credentials_wrong_creds(anyio_backend, db, create_user):
    await create_user(email="test", password="test")

    with pytest.raises(exceptions.WrongUsernameOrPasswordError):
        await user.services.authentication._verify_user_credentials(
            email="wrong",
            password="test",
            with_activation=False,
            conn=db,
        )

    with pytest.raises(exceptions.WrongUsernameOrPasswordError):
        await user.services.authentication._verify_user_credentials(
            email="test",
            password="wrong",
            with_activation=False,
            conn=db,
        )
