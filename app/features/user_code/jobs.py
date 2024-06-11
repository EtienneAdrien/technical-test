import asyncio
import random

from arq import Retry

from app.features.user_code import crud
from app.logging import logger


class RetryableMailError(Exception):
    pass


async def send_mail(email, user_code):
    """
    Fake sending an email by waiting a random x seconds.
    """
    logger.debug(f"Sending mail to {email} with code {user_code}")

    await asyncio.sleep(random.randint(1, 5))


async def handle_post_user_creation_job(
    ctx: dict, email: str, user_id: int, user_code: str
) -> None:
    """
    Email the user and start the activation process right after.
    Args:
        ctx: Context, also containing the db connection.
        email: The user email.
        user_id: The user id.
        user_code: The user code.
    Returns:
        None
    """
    try:
        await send_mail(email, user_code)
    except RetryableMailError:
        raise Retry(defer=ctx["job_try"] * 5)

    await crud.start_activation(conn=ctx["db"], user_id=user_id, user_code=user_code)
