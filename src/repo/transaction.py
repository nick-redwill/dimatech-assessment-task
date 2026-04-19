from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from exceptions import DuplicateError, NotFoundError
from models.transaction import TransactionOrm
from schemas.transaction import TransactionCreate
from schemas.relations import TransactionRel


async def create_transaction(
    session: AsyncSession, transaction_in: TransactionCreate
) -> TransactionRel:
    try:
        transaction = TransactionOrm(
            **transaction_in.model_dump(exclude_unset=True)
        )
        session.add(transaction)
        await session.flush()
        return await get_transaction(session, transaction.id)

    except IntegrityError as e:
        orig = str(e).lower()
        if "unique" in orig or "duplicate" in orig:
            raise DuplicateError(
                f"Transaction {transaction_in.id} already exists"
            )

        raise


async def delete_transaction(
    session: AsyncSession, transaction_id: UUID
) -> bool:
    query = delete(TransactionOrm).where(TransactionOrm.id == transaction_id)
    result = await session.execute(query)
    return result.rowcount > 0


async def get_transaction(
    session: AsyncSession, transaction_id: UUID
) -> TransactionRel:
    query = (
        select(TransactionOrm)
        .where(TransactionOrm.id == transaction_id)
        .options(joinedload(TransactionOrm.account))
    )
    result = await session.execute(query)
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise NotFoundError(f"Transaction {transaction_id} not found")

    return TransactionRel.model_validate(transaction, from_attributes=True)


async def get_all_transactions(
    session: AsyncSession, offset: int = 0, limit: int = 100
) -> list[TransactionRel]:
    query = (
        select(TransactionOrm)
        .options(joinedload(TransactionOrm.account))
        .offset(offset)
        .limit(limit)
        .order_by(TransactionOrm.created_at.desc())
    )
    result = await session.execute(query)
    transactions = result.scalars().all()

    return [
        TransactionRel.model_validate(t, from_attributes=True)
        for t in transactions
    ]


async def get_transactions_by_account(
    session: AsyncSession, account_id: UUID, offset: int = 0, limit: int = 100
) -> list[TransactionRel]:
    query = (
        select(TransactionOrm)
        .where(TransactionOrm.account_id == account_id)
        .options(joinedload(TransactionOrm.account))
        .offset(offset)
        .limit(limit)
        .order_by(TransactionOrm.created_at.desc())
    )
    result = await session.execute(query)
    transactions = result.scalars().all()
    return [
        TransactionRel.model_validate(t, from_attributes=True)
        for t in transactions
    ]
