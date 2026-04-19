from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase

from settings import DB_HOST, DB_PORT, DB_NAME, DB_PASS, DB_USER

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


class Base(DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_tables(engine):
    from models.account import AccountOrm
    from models.transaction import TransactionOrm
    from models.user import UserOrm

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
