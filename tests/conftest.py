from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy import event
from sqlalchemy.engine import Engine

from db import create_tables

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(DATABASE_URL, echo=False)
    await create_tables(engine)

    yield engine
    await engine.dispose()


@pytest.fixture
async def session(engine) -> AsyncGenerator[AsyncSession]:
    connection = await engine.connect()
    trans = await connection.begin()

    Session = async_sessionmaker(
        connection, expire_on_commit=False, class_=AsyncSession
    )
    async_session = Session()

    yield async_session

    await async_session.close()
    if trans.is_active:
        await trans.rollback()

    await connection.close()
