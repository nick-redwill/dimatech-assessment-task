from typing import TypeVar, Type

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from schemas.user import UserCreate, UserUpdate, UserInternal
from schemas.relations import UserRel
from models.user import UserOrm
from utils.auth import hash_password

UserSchema = TypeVar("UserSchema", UserRel, UserInternal)


async def create_user(session: AsyncSession, user_in: UserCreate) -> UserRel:
    data = user_in.model_dump()
    data["hashed_password"] = hash_password(data.pop("password"))

    user = UserOrm(**data)
    session.add(user)
    await session.flush()
    return await get_user(session, user.id)


async def update_user(
    session: AsyncSession, user_id: int, user_in: UserUpdate
) -> UserRel:
    data = user_in.model_dump(exclude_unset=True)
    if "password" in data:
        data["hashed_password"] = hash_password(data.pop("password"))

    query = (
        update(UserOrm)
        .where(UserOrm.id == user_id)
        .values(**data)
        .returning(UserOrm.id)
    )
    result = await session.execute(query)
    updated_id = result.scalar_one_or_none()

    if not updated_id:
        raise ValueError(f"User with id {user_id} not found")

    await session.flush()
    return await get_user(session, updated_id)


async def delete_user(session: AsyncSession, user_id: int) -> bool:
    query = delete(UserOrm).where(UserOrm.id == user_id)
    result = await session.execute(query)
    return result.rowcount > 0


async def get_user(
    session: AsyncSession,
    user_id: int,
    schema: Type[UserSchema] = UserRel,
) -> Type[UserSchema]:
    query = (
        select(UserOrm)
        .where(UserOrm.id == user_id)
        .options(selectinload(UserOrm.account))
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise ValueError(f"User with id {user_id} not found")

    return schema.model_validate(user, from_attributes=True)


async def get_user_by_email(
    session: AsyncSession,
    email: str,
    schema: Type[UserSchema] = UserRel,
) -> Type[UserSchema]:
    query = (
        select(UserOrm)
        .where(UserOrm.email == email)
        .options(selectinload(UserOrm.account))
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise ValueError(f"User with email {email} not found")

    return schema.model_validate(user, from_attributes=True)


async def get_all_users(
    session: AsyncSession, offset: int = 0, limit: int = 100
) -> list[UserRel]:
    query = (
        select(UserOrm)
        .options(selectinload(UserOrm.account))
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(query)
    users = result.scalars().all()

    return [UserRel.model_validate(u, from_attributes=True) for u in users]
