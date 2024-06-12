import asyncio
import functools
import random

from arq import Retry
from arq.jobs import Job

from app import config
from app.features.user_code import crud
from app.logging import logger


class RetryableMailError(Exception):
    pass


async def send_mail(email, user_code):
    """
    Fake sending an email by waiting a random x seconds.
    """
    logger.debug(f"Sending mail to {email} with code {user_code}")

    if config.FORCE_JOB_TO_FAIL:
        raise RetryableMailError

    await asyncio.sleep(random.randint(1, 5))


def requeue_failed_jobs_on_max_retry_in_dead_letter(func):
    """
    A decorator that requeues failed jobs if the maximum number of retries is reached in the dead letter queue.

    Args:
        func: the original function to be wrapped

    Returns:
        the wrapper function that handles retry logic
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        ctx = args[0]

        try:
            return await func(*args, **kwargs)
        except Retry as e:
            if ctx["job_try"] >= config.WORKER_MAX_TRIES:
                await Job(job_id=ctx["job_id"], redis=ctx["redis"]).abort()

                await ctx["redis"].enqueue_job(
                    "dead_letter",
                    **kwargs,
                    _queue_name="dead_letter",
                )
            else:
                raise e

    return wrapper


async def handle_post_user_creation_job(
    ctx: dict,
    email: str,
    user_id: int,
    user_code: str,
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
        raise Retry(defer=ctx["job_try"] * config.JOB_RETRY_DELAY)

    await crud.start_activation(conn=ctx["db"], user_id=user_id, user_code=user_code)
