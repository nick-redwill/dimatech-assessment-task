import pytest
import pytest_asyncio
from uuid import uuid4

from services.transaction import process_webhook
from decimal import Decimal

from repo.account import get_account
from repo.user import create_user

from schemas.user import UserCreate

from exceptions import DuplicateError


@pytest_asyncio.fixture
async def setup_user(session):
    user_data = UserCreate(
        email="test@mail.com",
        password="test",
        full_name="Test User",
    )
    user = await create_user(session, user_data)
    return user


@pytest.mark.asyncio
async def test_process_webhook_creates_transaction(session, setup_user):
    account_id = uuid4()
    tx = await process_webhook(
        session, str(uuid4()), account_id, setup_user.id, Decimal("100")
    )
    assert tx.amount == Decimal("100")
    assert tx.account.balance == Decimal("100")


@pytest.mark.asyncio
async def test_process_webhook_creates_account_if_missing(session, setup_user):
    account_id = uuid4()
    await process_webhook(
        session, str(uuid4()), account_id, setup_user.id, Decimal("50")
    )
    account = await get_account(session, account_id)
    assert account is not None


@pytest.mark.asyncio
async def test_process_webhook_duplicate_transaction(session, setup_user):
    account_id = uuid4()
    transaction_id = str(uuid4())
    await process_webhook(
        session, transaction_id, account_id, setup_user.id, Decimal("100")
    )
    with pytest.raises(DuplicateError):
        await process_webhook(
            session, transaction_id, account_id, setup_user.id, Decimal("100")
        )


@pytest.mark.asyncio
async def test_process_webhook_accumulates_balance(session, setup_user):
    account_id = uuid4()
    await process_webhook(
        session, str(uuid4()), account_id, setup_user.id, Decimal("100")
    )
    await process_webhook(
        session, str(uuid4()), account_id, setup_user.id, Decimal("50")
    )
    account = await get_account(session, account_id)
    assert account.balance == Decimal("150")
