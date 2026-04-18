from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.account import AccountOrm
from schemas.account import AccountCreate, AccountUpdate
from schemas.relations import AccountRel


async def create_account(
    session: AsyncSession, account_in: AccountCreate
) -> AccountRel:
    account = AccountOrm(**account_in.model_dump())
    session.add(account)
    await session.flush()
    return await get_account(session, account.id)


async def update_account(
    session: AsyncSession, account_id: UUID, account_in: AccountUpdate
) -> AccountRel:
    query = (
        update(AccountOrm)
        .where(AccountOrm.id == account_id)
        .values(**account_in.model_dump(exclude_unset=True))
        .returning(AccountOrm.id)
    )
    result = await session.execute(query)
    updated_id = result.scalar_one_or_none()

    if not updated_id:
        raise ValueError(f"Account with id {account_id} not found")

    await session.flush()
    return await get_account(session, updated_id)


async def delete_account(session: AsyncSession, account_id: UUID) -> bool:
    query = delete(AccountOrm).where(AccountOrm.id == account_id)
    result = await session.execute(query)
    return result.rowcount > 0


async def get_account(session: AsyncSession, account_id: UUID) -> AccountRel:
    query = (
        select(AccountOrm)
        .where(AccountOrm.id == account_id)
        .options(joinedload(AccountOrm.user))
    )
    result = await session.execute(query)
    account = result.scalar_one_or_none()

    if not account:
        raise ValueError(f"Account with id {account_id} not found")

    return AccountRel.model_validate(account, from_attributes=True)


async def get_all_accounts(
    session: AsyncSession, offset: int = 0, limit: int = 100
) -> list[AccountRel]:
    query = (
        select(AccountOrm)
        .options(joinedload(AccountOrm.user))
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(query)
    accounts = result.scalars().all()

    return [
        AccountRel.model_validate(a, from_attributes=True) for a in accounts
    ]
