from typing import Annotated

from arq import ArqRedis
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from fastapi import status
from fastapi.security import HTTPBasicCredentials
from psycopg_pool.abc import ACT

from app import config
from app.features import user_code, user
from app.features.schemas import Success, UnexpectedError
from app.features.user import schemas, crud, exceptions
from app.features.user_code.exceptions import (
    InvalidUserCodeError,
    ExpiredUserCodeError,
    UserAlreadyActivatedError,
)
from app.logging import logger
from app.utils.db.connect import get_db
from app.utils.redis.connect import get_redis

router = APIRouter(
    prefix="/user", tags=["Users"], responses={500: {"model": UnexpectedError}}
)


@router.post("/")
async def create_user(
    user_: Annotated[schemas.UserIn, Body(alias="user")],
    db: ACT = Depends(get_db),
    redis: ArqRedis = Depends(get_redis),
) -> schemas.UserCreatedResponse:
    """
    Create a new user, this will also create a user code associated with it, an async job will then be enqueued to
    email the user with his code, so he can activate his account.
    """
    logger.debug(f"Creating user {user_.email}")

    try:
        user_id, user_code_ = await crud.create_user_with_code(user=user_, conn=db)
    except exceptions.UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    await redis.enqueue_job(
        function="handle_post_user_creation_job",
        email=user_.email,
        user_id=user_id,
        user_code=user_code_,
        _queue_name=config.QUEUE_NAME,
    )

    logger.info(f"User {user_id} successfully created with code {user_code_}")

    return schemas.UserCreatedResponse(user_id=user_id)


@router.get("/validate")
async def validate_user(
    credentials: Annotated[
        HTTPBasicCredentials,
        Depends(user.services.authentication.auth_unvalidated_user),
    ],
    user_code_: Annotated[str, Query(alias="user_code")],
    db: ACT = Depends(get_db),
) -> Success:
    """
    Validate a user code, first authenticate the user with his email and password and then verify the user code.
    """
    try:
        await user_code.services.validation.validate_user(
            user_code=user_code_, user_email=credentials.username, conn=db
        )

    except InvalidUserCodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user code",
        )
    except ExpiredUserCodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expired user code",
        )
    except UserAlreadyActivatedError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already activated",
        )

    return Success(message="User successfully activated")


@router.get("/")
def test_user_connection(
    credentials: Annotated[
        HTTPBasicCredentials, Depends(user.services.authentication.auth_user)
    ]
) -> schemas.TestUserResponse:
    """
    Test the user connection, by authenticating the user with his email and password and verifying that he is activated.
    """
    return schemas.TestUserResponse(
        user_email=credentials.username,
    )
