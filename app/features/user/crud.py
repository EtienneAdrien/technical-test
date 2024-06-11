from psycopg_pool.abc import ACT

from app.features.user import schemas, exceptions
from app.features.user_code.crud import create_user_code
from app.utils import security


async def create_user_with_code(conn: ACT, user: schemas.UserIn) -> (int, str):
    """
    Create a user with an activation code.

    Note that the password is hashed before it is inserted into the database.

    Returns:
        user_id, user_code: The user_id and the activation code.
    """
    cursor = conn.cursor()
    password = security.hash_password(user.password)

    async with conn.transaction():
        await cursor.execute(
            "INSERT INTO user_data (email, password) VALUES (%s, %s) RETURNING user_id",
            (user.email, password),
        )

        result = await cursor.fetchone()
        user_id = result[0]

        user_code = await create_user_code(user_id=user_id, conn=conn)

    return user_id, user_code


async def update_user_activation(user_id: int, db: ACT, activated: bool = True):
    """
    Update the activation status of a user.

    Returns:
        None
    """
    cursor = db.cursor()
    await cursor.execute(
        "UPDATE user_data SET activated = %s WHERE user_id = %s RETURNING user_id",
        (
            activated,
            user_id,
        ),
    )

    user_id = await cursor.fetchone()

    if not user_id:
        raise exceptions.UserNotFoundError()

    await db.commit()


async def get_user_by_email(email: str, conn: ACT) -> schemas.UserInternal | None:
    """
    Get a user by email.

    Returns None if the user does not exist.

    Returns:
        None
    """
    cursor = conn.cursor()
    await cursor.execute(
        "SELECT user_data.user_id, user_data.password, user_data.activated FROM user_data WHERE email = %s",
        (email,),
    )

    result = await cursor.fetchone()

    if result is None:
        return None

    return schemas.UserInternal(
        user_id=result[0], password=result[1], activated=result[2], email=email
    )
