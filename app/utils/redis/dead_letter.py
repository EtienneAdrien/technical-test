import logging

log = logging.getLogger("arq")


async def dead_letter(ctx, *args, **kwargs):
    log.info(f"Following job failed: {ctx['job_id']}")
