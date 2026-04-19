from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.account import AccountCreate, AccountUpdate
from schemas.relations import AccountRel
from repo import account as account_repo


async def get_account(session: AsyncSession, account_id: UUID) -> AccountRel:
    return await account_repo.get_account(session, account_id)


async def get_all_accounts(
    session: AsyncSession, offset: int = 0, limit: int = 100
) -> list[AccountRel]:
    return await account_repo.get_all_accounts(
        session, offset=offset, limit=limit
    )


async def get_user_accounts(
    session: AsyncSession, user_id: int, offset: int = 0, limit: int = 100
) -> list[AccountRel]:
    return await account_repo.get_accounts_by_user(
        session, user_id, offset=offset, limit=limit
    )


async def create_account(
    session: AsyncSession, account_in: AccountCreate
) -> AccountRel:
    return await account_repo.create_account(session, account_in)


async def update_account(
    session: AsyncSession, account_id: UUID, account_in: AccountUpdate
) -> AccountRel:
    return await account_repo.update_account(session, account_id, account_in)


async def delete_account(session: AsyncSession, account_id: UUID) -> bool:
    return await account_repo.delete_account(session, account_id)
