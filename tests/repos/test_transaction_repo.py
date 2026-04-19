from uuid import uuid4
from decimal import Decimal

import pytest
import pytest_asyncio

from exceptions import DuplicateError, NotFoundError
from schemas.transaction import TransactionCreate
from schemas.account import AccountCreate
from schemas.user import UserCreate
from repo.user import create_user
from repo.account import create_account
from repo.transaction import (
    create_transaction,
    get_transaction,
    get_transactions_by_account,
    get_all_transactions,
    delete_transaction,
)


@pytest_asyncio.fixture
async def setup_account(session):
    user_data = UserCreate(
        email="test@mail.com",
        password="test",
        full_name="Test User",
    )
    user = await create_user(session, user_data)

    account_data = AccountCreate(user_id=user.id, balance=Decimal("1000.00"))
    account = await create_account(session, account_data)

    return account


@pytest.mark.asyncio
async def test_create_transaction(session, setup_account):
    tx_data = TransactionCreate(
        account_id=setup_account.id, amount=Decimal("250.75")
    )

    tx = await create_transaction(session, tx_data)

    assert tx.id is not None
    assert tx.amount == Decimal("250.75")
    assert tx.account.id == setup_account.id

    assert tx.account.user_id == setup_account.user_id


@pytest.mark.asyncio
async def test_get_transaction(session, setup_account):
    tx = await create_transaction(
        session,
        TransactionCreate(
            account_id=setup_account.id, amount=Decimal("50.00")
        ),
    )

    fetched = await get_transaction(session, tx.id)
    assert fetched.id == tx.id
    assert fetched.amount == Decimal("50.00")


@pytest.mark.asyncio
async def test_create_duplicate_transaction(session, setup_account):
    tx = await create_transaction(
        session,
        TransactionCreate(
            account_id=setup_account.id, amount=Decimal("50.00")
        ),
    )

    with pytest.raises(DuplicateError):
        await create_transaction(
            session,
            TransactionCreate(
                id=tx.id,
                account_id=setup_account.id,
                amount=Decimal("50.00"),
            ),
        )


@pytest.mark.asyncio
async def test_get_transactions_by_account(session, setup_account):
    for i in range(3):
        await create_transaction(
            session,
            TransactionCreate(
                account_id=setup_account.id, amount=Decimal(str(i * 10))
            ),
        )

    account2 = await create_account(
        session,
        AccountCreate(user_id=setup_account.user_id, balance=Decimal("0.00")),
    )

    for i in range(3):
        await create_transaction(
            session,
            TransactionCreate(
                account_id=account2.id, amount=Decimal(str(i * 10))
            ),
        )

    transactions = await get_transactions_by_account(session, setup_account.id)

    assert len(transactions) == 3
    for tx in transactions:
        assert tx.account_id == setup_account.id
        assert tx.account is not None


@pytest.mark.asyncio
async def test_get_all_transactions(session, setup_account):
    for i in range(10):
        await create_transaction(
            session,
            TransactionCreate(account_id=setup_account.id, amount=Decimal(i)),
        )

    txs = await get_all_transactions(session, limit=5)
    assert len(txs) == 5

    txs = await get_all_transactions(session, offset=3)
    assert len(txs) == 7

    txs = await get_all_transactions(session)
    for tx in txs:
        assert tx.account.id == setup_account.id


@pytest.mark.asyncio
async def test_create_transaction_invalid_account(session):
    invalid_data = TransactionCreate(
        account_id=uuid4(), amount=Decimal("100.00")
    )

    with pytest.raises(Exception):
        await create_transaction(session, invalid_data)
        await session.flush()


@pytest.mark.asyncio
async def test_delete_transaction(session, setup_account):
    tx = await create_transaction(
        session,
        TransactionCreate(account_id=setup_account.id, amount=Decimal("1.00")),
    )

    result = await delete_transaction(session, tx.id)
    assert result is True

    with pytest.raises(NotFoundError, match="not found"):
        await get_transaction(session, tx.id)
