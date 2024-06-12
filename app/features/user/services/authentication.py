from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi import status
from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials
from psycopg_pool.abc import ACT

from app import logging
from app.features.user import crud, exceptions
from app.logging import logger
from app.utils import security
from app.utils.db.connect import get_db

http_basic = HTTPBasic()


async def _verify_user_credentials(
    email: str,
    password: str,
    conn: ACT,
    with_activation: bool = True,
) -> None:
    """
    Private function to verify user credentials.

    Raises:
        exceptions.WrongUsernameOrPasswordError:
            If user not found or password is wrong
        exceptions.UserNotActivatedError:
            If user is not activated

    Args:
        email: Email of the user
        password: Password of the user
        conn: Connection
        with_activation: Whether to raise an exception if user is not activated

    Returns:
        None
    """
    user_obj = await crud.get_user_by_email(email=email, conn=conn)

    if not user_obj:
        raise exceptions.WrongUsernameOrPasswordError()

    is_correct = security.check_hash(password=password, hash_=user_obj.password)

    if not is_correct:
        raise exceptions.WrongUsernameOrPasswordError()

    if not user_obj.activated and with_activation:
        raise exceptions.UserNotActivatedError()


async def _connect_user(
    with_activation: bool,
    credentials: Annotated[HTTPBasicCredentials, Depends(http_basic)],
    db: ACT = Depends(get_db),
) -> HTTPBasicCredentials:
    """
    Wrapper around _verify_user_credentials to raise HTTPException on error.
    """
    logger.info(f"Authenticating user {credentials.username}")

    try:
        await _verify_user_credentials(
            email=credentials.username,
            password=credentials.password,
            conn=db,
            with_activation=with_activation,
        )

        logger.info(f"User {credentials.username} successfully authenticated")

    except exceptions.WrongUsernameOrPasswordError:
        logger.error("Failed to authenticate user, wrong username or password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    except exceptions.UserNotActivatedError:
        logger.error("Failed to authenticate user, user not activated")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not activated",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials


async def auth_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(http_basic)],
    db: ACT = Depends(get_db),
):
    """
    Dependency injected function to authenticate a validated user.
    """
    return await _connect_user(with_activation=True, credentials=credentials, db=db)


async def auth_unvalidated_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(http_basic)],
    db: ACT = Depends(get_db),
):
    """
    Dependency injected function to authenticate an unvalidated user.
    """
    return await _connect_user(with_activation=False, credentials=credentials, db=db)
