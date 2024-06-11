import pytest
from arq import Retry

from app.features.user_code import jobs


async def test_handle_post_user_creation_job(
    anyio_backend, db, create_user, create_user_code
):
    user_id = await create_user(email="test", password="test")
    code = await create_user_code(user_id=user_id)

    await jobs.handle_post_user_creation_job(
        ctx={"job_try": 1, "db": db}, email="test", user_id=user_id, user_code=code
    )


async def test_handle_post_user_creation_job_mail_failed_but_retryable(
    anyio_backend, monkeypatch_session, redis, db, create_user, create_user_code
):
    async def send_mail(_, __):
        raise jobs.RetryableMailError

    monkeypatch_session.setattr(jobs, "send_mail", send_mail)

    user_id = await create_user(email="test", password="test")
    code = await create_user_code(user_id=user_id)

    with pytest.raises(Retry):
        await jobs.handle_post_user_creation_job(
            ctx={"job_try": 1, "db": db}, email="test", user_id=user_id, user_code=code
        )
