import datetime

import psycopg
from psycopg_pool.abc import ACT

from app.features.user.exceptions import UserNotFoundError
from app.features.user_code import utils, schemas, exceptions


async def create_user_code(conn: ACT, user_id: int) -> str:
    """
    Generate and create a code for a user given his id.

    Raises
        UserNotFoundError: Raised if the user does not exist

    Returns:
        code: The generated code
    """
    code = utils.generate_code()

    cursor = conn.cursor()

    try:
        await cursor.execute(
            "INSERT INTO user_code (user_id, code) VALUES (%s, %s)",
            (
                user_id,
                code,
            ),
        )
    except psycopg.errors.ForeignKeyViolation:
        raise UserNotFoundError()

    return code


async def start_activation(conn: ACT, user_id: int, user_code: str) -> None:
    """
    Start the activation of a user given his id and code.

    Raises:
        UserCodeNotFoundError: Raised if the user code does not exist

    Returns:
        None
    """
    cursor = conn.cursor()

    await cursor.execute(
        "UPDATE user_code SET date_start_validity = %s WHERE user_id = %s AND code = %s RETURNING user_id",
        (datetime.datetime.now(datetime.UTC), user_id, user_code),
    )

    user_id = await cursor.fetchone()

    if not user_id:
        raise exceptions.UserCodeNotFoundError()

    await conn.commit()


async def get_user_code(user_email: str, user_code: str, conn: ACT) -> schemas.UserCode:
    """
    Get a user code information from a user, given his email and code.

    Raises:
        UserCodeNotFoundError: Raised if the user code does not exist.

    Returns:
        schemas.UserCode: The user code information
    """
    cursor = conn.cursor()
    await cursor.execute(
        """
        SELECT user_data.user_id, user_code.code, user_code.date_start_validity, user_data.activated 
        FROM user_data JOIN user_code ON user_code.user_id = user_data.user_id 
        WHERE user_data.email = %s
        AND user_code.code = %s
    """,
        (user_email, user_code),
    )

    result = await cursor.fetchone()

    if not result:
        raise exceptions.UserCodeNotFoundError()

    if result[3]:
        raise exceptions.UserAlreadyActivatedError()

    return schemas.UserCode(
        user_id=result[0],
        code=result[1],
        date_start_validity=result[2],
    )
