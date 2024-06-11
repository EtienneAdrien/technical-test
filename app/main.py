from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from starlette.responses import JSONResponse

from app.routers import user
from app.utils.db.connect import connection_pool
from app.utils.db.init import init_database_schema
from app.utils.redis.connect import redis_pool


@asynccontextmanager
async def lifespan(_):
    """
    Start the database and redis connections, initialize the database schema and close connections on app shutdown.
    """
    await redis_pool().startup()
    await init_database_schema()
    await connection_pool().open()

    yield
    await connection_pool().close()


app = FastAPI(lifespan=lifespan, title="Technical Test", version="1.0.0")
app.include_router(user.router)


@app.exception_handler(Exception)
async def validation_exception_handler(request, exc) -> JSONResponse:
    """
    Simple error handler for unhandled exceptions.
    """
    return JSONResponse(
        content={
            "status": "error",
            "message": "An unexpected error occurred",
        },
        status_code=500,
    )


app.add_middleware(CorrelationIdMiddleware)
