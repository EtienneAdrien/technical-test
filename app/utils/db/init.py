import psycopg

from app import config, ROOT_PATH
from app.logging import logger


async def create_main_db(dbname: str):
    conn = await connect_default_db()

    await conn.set_autocommit(True)

    async with conn.cursor() as cur:
        await cur.execute(f"""CREATE DATABASE "{dbname}";""")
        await conn.commit()


async def init_schema(conn):
    await conn.set_autocommit(True)

    with open(ROOT_PATH / "utils" / "db" / "init.sql") as f:
        sql = f.read()
        async with conn.cursor() as cur:
            await cur.execute(sql)
            await conn.commit()


async def connect_main_db(dbname: str):
    return await psycopg.AsyncConnection.connect(
        f"""dbname={dbname}
        user={config.POSTGRES_USER} 
        password={config.POSTGRES_PASSWORD} 
        host={config.POSTGRES_HOST} 
        port={config.POSTGRES_PORT}"""
    )


async def connect_default_db():
    return await psycopg.AsyncConnection.connect(
        f"""dbname=postgres
        user={config.POSTGRES_USER} 
        password={config.POSTGRES_PASSWORD} 
        host={config.POSTGRES_HOST} 
        port={config.POSTGRES_PORT}"""
    )


async def init_database_schema():
    dbname = config.POSTGRES_DB

    try:
        logger.debug(f"Connecting to main database {dbname}")
        await connect_main_db(dbname=dbname)

    except psycopg.OperationalError:
        logger.debug(
            f"Failed to connect to main database. Creating main database {dbname}"
        )
        await create_main_db(dbname=dbname)

        logger.debug("Connecting to main database again")
        conn = await connect_main_db(dbname=dbname)

        logger.debug("Creating schema")
        await init_schema(conn=conn)

    logger.debug(f"Successfully connected to main database {dbname}")


async def delete_database():
    conn = await connect_default_db()

    await conn.set_autocommit(True)
    await conn.execute(f'DROP DATABASE "{config.POSTGRES_DB}" WITH (FORCE)')
    await conn.commit()
