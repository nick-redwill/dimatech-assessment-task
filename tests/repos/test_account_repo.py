from uuid import uuid4
from decimal import Decimal

import pytest
import pytest_asyncio

from schemas.account import AccountCreate, AccountUpdate
from schemas.user import UserCreate
from repo.user import create_user
from repo.account import (
    create_account,
    get_account,
    update_account,
    delete_account,
    get_all_accounts,
)


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
async def test_create_account(session, setup_user):
    account_data = AccountCreate(
        user_id=setup_user.id, balance=Decimal("150.50")
    )
    account = await create_account(session, account_data)

    assert account.user_id == setup_user.id
    assert account.balance == Decimal("150.50")
    assert account.user is not None
    assert account.user.email == "test@mail.com"


@pytest.mark.asyncio
async def test_update_account(session, setup_user):
    account = await create_account(
        session, AccountCreate(user_id=setup_user.id, balance=Decimal("10.00"))
    )

    update_data = AccountUpdate(balance=Decimal("1000.00"))
    updated = await update_account(session, account.id, update_data)

    assert updated.balance == Decimal("1000.00")

    fetched = await get_account(session, account.id)
    assert fetched.balance == Decimal("1000.00")


@pytest.mark.asyncio
async def test_update_non_existent_account(session):
    random_uuid = uuid4()
    with pytest.raises(ValueError, match="not found"):
        await update_account(session, random_uuid, AccountUpdate(balance=100))


@pytest.mark.asyncio
async def test_delete_account(session, setup_user):
    account = await create_account(
        session, AccountCreate(user_id=setup_user.id)
    )

    deleted = await delete_account(session, account.id)
    assert deleted is True

    with pytest.raises(ValueError, match="not found"):
        await get_account(session, account.id)


@pytest.mark.asyncio
async def test_get_account_not_found(session):
    random_uuid = uuid4()
    with pytest.raises(ValueError, match="not found"):
        await get_account(session, random_uuid)


@pytest.mark.asyncio
async def test_get_all_accounts_list(session, setup_user):
    for _ in range(10):
        await create_account(session, AccountCreate(user_id=setup_user.id))

    accounts = await get_all_accounts(session, limit=5)
    assert len(accounts) == 5

    accounts = await get_all_accounts(session, offset=3)
    assert len(accounts) == 7

    accounts = await get_all_accounts(session)
    for acc in accounts:
        assert acc.user.email == setup_user.email
