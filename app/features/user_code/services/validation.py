import datetime

from psycopg_pool.abc import ACT

from app import config
from app.features import user
from app.features.user_code import crud, exceptions, schemas
from app.logging import logger


async def _is_user_code_valid(
    user_email: str, user_code: str, conn: ACT
) -> schemas.UserCode:
    """
    Private function to verify user credentials.

    Raises:
        exceptions.UserCodeAvailabilityNeverStartedError:
            If user code availability never started, this would mean that the mail has never been sent.
        exceptions.ExpiredUserCodeError:
            If the user code is expired.
        exceptions.UserCodeNotFoundError:
            If the user/user code does not exist.

    Returns:
        schemas.UserCode: Return the user code information if the code is valid.
    """
    logger.debug(
        f"Checking if user code is valid for user {user_email} and code {user_code}"
    )
    user_code_obj = await crud.get_user_code(
        user_email=user_email, user_code=user_code, conn=conn
    )

    now = datetime.datetime.now(datetime.UTC)

    if not user_code_obj.date_start_validity:
        logger.debug("User code availability never started")
        raise exceptions.UserCodeAvailabilityNeverStartedError()

    elapsed_time_in_ms = (
        now - user_code_obj.date_start_validity
    ).total_seconds() * 1000

    if elapsed_time_in_ms > config.USER_CODE_VALIDITY_MS:
        logger.debug(f"Code expired since {round(elapsed_time_in_ms / 1000)} seconds")
        raise exceptions.ExpiredUserCodeError()
    else:
        logger.debug("User code is valid")
        return user_code_obj


async def validate_user(user_email: str, user_code: str, conn: ACT) -> None:
    """
    If the user code is valid, activate the user.
    """
    user_code_obj = await _is_user_code_valid(user_email, user_code, conn)
    await user.crud.update_user_activation(user_id=user_code_obj.user_id, db=conn)
