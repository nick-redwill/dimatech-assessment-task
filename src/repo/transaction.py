from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.transaction import TransactionOrm
from schemas.transaction import TransactionCreate
from schemas.relations import TransactionRel


async def create_transaction(
    session: AsyncSession, transaction_in: TransactionCreate
) -> TransactionRel:
    transaction = TransactionOrm(**transaction_in.model_dump())
    session.add(transaction)
    await session.flush()
    return await get_transaction(session, transaction.id)


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
        raise ValueError(f"Transaction {transaction_id} not found")

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
