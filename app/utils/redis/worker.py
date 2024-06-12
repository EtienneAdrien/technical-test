import arq

from app import config
from app.features.user_code.jobs import (
    handle_post_user_creation_job,
    requeue_failed_jobs_on_max_retry_in_dead_letter,
)
from app.utils.db.connect import connection_pool
from app.utils.redis.connect import REDIS_SETTINGS
from app.utils.redis.dead_letter import dead_letter


async def on_startup(ctx: dict) -> dict:
    """
    Pass the db connection to the context, so it can be used in the worker easily
    Args:
        ctx: The context for the worker

    Returns:
        The context
    """
    await connection_pool().open()
    ctx["db"] = await connection_pool().getconn()

    return ctx


async def on_shutdown(ctx: dict) -> dict:
    """
    Closes the db connection.
    Args:
        ctx: The context for the worker

    Returns:
        The context
    """
    await connection_pool().close()
    await connection_pool().putconn(ctx["db"])

    return ctx


class WorkerSettings(arq.Worker):
    functions = [
        requeue_failed_jobs_on_max_retry_in_dead_letter(handle_post_user_creation_job)
    ]
    redis_settings = REDIS_SETTINGS()
    max_tries = config.WORKER_MAX_TRIES
    queue_name = config.QUEUE_NAME

    allow_abort_jobs = True

    on_startup = on_startup
    on_shutdown = on_shutdown


class DeadLetterSettings(arq.Worker):
    functions = [dead_letter]
    redis_settings = REDIS_SETTINGS()
    max_tries = config.WORKER_MAX_TRIES

    queue_name = "dead_letter"

    allow_abort_jobs = True

    on_startup = on_startup
    on_shutdown = on_shutdown
