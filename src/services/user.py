from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import UserCreate, UserUpdate, UserInternal
from schemas.account import AccountCreate
from schemas.relations import UserRel

from repo import user as user_repo
from repo import account as account_repo

from utils.auth import verify_password, create_jwt_token

from exceptions import NotFoundError, PermissionError, AuthError


async def authenticate_user(
    session: AsyncSession,
    email: str,
    password: str,
):
    try:
        user = await user_repo.get_user_by_email(session, email, UserInternal)
    except NotFoundError:
        raise AuthError("Invalid credentials")

    if not verify_password(password, user.hashed_password):
        raise AuthError("Invalid credentials")

    return create_jwt_token(
        {
            "sub": str(user.id),
            "role": user.role.value,
        }
    )


async def create_user_with_default_account(
    session: AsyncSession, user_in: UserCreate
) -> UserRel:
    user = await user_repo.create_user(session, user_in)
    await account_repo.create_account(
        session,
        AccountCreate(
            user_id=user.id,
        ),
    )

    return await user_repo.get_user(session, user.id)


async def delete_user(session: AsyncSession, user_id: int) -> bool:
    return await user_repo.delete_user(session, user_id)


async def update_user(
    session: AsyncSession, user_id: int, user_in: UserUpdate
):
    return await user_repo.update_user(session, user_id, user_in)


async def get_user(session: AsyncSession, user_id: int) -> UserRel:
    return await user_repo.get_user(session, user_id)


async def get_all_users(
    session: AsyncSession, offset: int = 0, limit: int = 100
):
    return await user_repo.get_all_users(session, offset, limit)
