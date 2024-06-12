import os

USER_CODE_VALIDITY_MS = int(os.environ["USER_CODE_VALIDITY_MS"])
WORKER_MAX_TRIES = int(os.environ["WORKER_MAX_TRIES"])
QUEUE_NAME = os.environ["QUEUE_NAME"]
FORCE_JOB_TO_FAIL = int(os.environ["FORCE_JOB_TO_FAIL"])
JOB_RETRY_DELAY = int(os.environ["JOB_RETRY_DELAY"])

REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ["REDIS_PORT"])
REDIS_DB = int(os.environ["REDIS_DB"])
REDIS_PASSWORD = os.environ["REDIS_PASSWORD"]

POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_HOST = os.environ["POSTGRES_HOST"]
POSTGRES_PORT = int(os.environ["POSTGRES_PORT"])
