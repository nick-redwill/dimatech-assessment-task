from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import NotFoundError
from schemas.account import AccountCreate, AccountUpdate
from schemas.transaction import TransactionCreate
from schemas.relations import TransactionRel
from repo import transaction as transaction_repo
from repo import account as account_repo


async def get_transaction(
    session: AsyncSession, transaction_id: UUID
) -> TransactionRel:
    return await transaction_repo.get_transaction(session, transaction_id)


async def get_all_transactions(
    session: AsyncSession, offset: int = 0, limit: int = 100
) -> list[TransactionRel]:
    return await transaction_repo.get_all_transactions(
        session, offset=offset, limit=limit
    )


async def get_user_transactions(
    session: AsyncSession, user_id: int, offset: int = 0, limit: int = 100
) -> list[TransactionRel]:
    accounts = await account_repo.get_accounts_by_user(session, user_id)
    all_transactions = []

    for account in accounts:
        txs = await transaction_repo.get_transactions_by_account(
            session, account.id, offset=offset, limit=limit
        )
        all_transactions.extend(txs)

    return all_transactions


async def process_webhook(
    session: AsyncSession,
    transaction_id: str,
    account_id: UUID,
    user_id: int,
    amount: Decimal,
) -> TransactionRel:
    try:
        account = await account_repo.get_account(session, account_id)
    except NotFoundError:
        account = await account_repo.create_account(
            session,
            AccountCreate(id=account_id, user_id=user_id),
        )

    transaction = await transaction_repo.create_transaction(
        session,
        TransactionCreate(
            id=transaction_id,
            account_id=account.id,
            amount=amount,
        ),
    )

    await account_repo.update_account(
        session,
        account.id,
        AccountUpdate(balance=account.balance + amount),
    )

    return await transaction_repo.get_transaction(session, transaction.id)
