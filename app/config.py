import os

USER_CODE_VALIDITY_MS = os.environ.get("USER_CODE_VALIDITY_MS", 60000)

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_DB = os.environ.get("REDIS_DB", 0)
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "redispass")

POSTGRES_DB = os.environ.get("POSTGRES_DB", "tech-test")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "database")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", 5432)
