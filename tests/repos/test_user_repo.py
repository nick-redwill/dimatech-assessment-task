import pytest

from schemas.user import UserCreate, UserUpdate, UserInternal
from repo.user import (
    create_user,
    get_user,
    get_user_by_email,
    delete_user,
    update_user,
    get_all_users,
)
from enums import UserRole
from utils.auth import verify_password


@pytest.mark.asyncio
async def test_create(session):
    user_data = UserCreate(
        email="test@mail.com",
        password="test",
        full_name="Test User",
    )
    user = await create_user(session, user_data)

    assert user.id is not None
    assert user.email == "test@mail.com"
    assert user.full_name == "Test User"
    assert user.role == UserRole.USER

    fetched = await get_user(session, user.id, schema=UserInternal)
    assert fetched.id == user.id
    assert fetched.email == "test@mail.com"
    assert verify_password("test", fetched.hashed_password)


@pytest.mark.asyncio
async def test_get_user_by_email(session):
    user_data = UserCreate(
        email="test@mail.com",
        password="test",
        full_name="Test User",
    )
    await create_user(session, user_data)

    user = await get_user_by_email(session, email="test@mail.com")
    assert user.email == "test@mail.com"
    assert user.full_name == "Test User"


@pytest.mark.asyncio
async def test_get_non_existent_user(session):
    with pytest.raises(ValueError, match="not found"):
        await get_user(session, 999)


@pytest.mark.asyncio
async def test_get_non_existent_user_by_email(session):
    with pytest.raises(ValueError, match="not found"):
        await get_user_by_email(session, "test@test.com")


@pytest.mark.asyncio
async def test_update_user(session):
    user = await create_user(
        session,
        UserCreate(
            email="original@mail.com",
            password="test",
            full_name="Original Name",
        ),
    )

    updated = await update_user(
        session,
        user.id,
        UserUpdate(full_name="Updated Name", role=UserRole.ADMIN),
    )

    assert updated.full_name == "Updated Name"
    assert updated.role == UserRole.ADMIN

    fetched = await get_user(session, user.id)
    assert fetched.full_name == "Updated Name"


@pytest.mark.asyncio
async def test_update_password(session):
    user = await create_user(
        session,
        UserCreate(
            email="pwtest@mail.com", password="oldpass", full_name="PW User"
        ),
    )

    await update_user(session, user.id, UserUpdate(password="newpass"))
    internal = await get_user(session, user.id, schema=UserInternal)
    assert not verify_password("oldpass", internal.hashed_password)
    assert verify_password("newpass", internal.hashed_password)


@pytest.mark.asyncio
async def test_update_non_existent(session):
    with pytest.raises(ValueError, match="not found"):
        await update_user(session, 999, UserUpdate(email="test@test.com"))


@pytest.mark.asyncio
async def test_delete_user(session):
    user = await create_user(
        session,
        UserCreate(
            email="delete@mail.com", password="test", full_name="To Delete"
        ),
    )

    is_deleted = await delete_user(session, user.id)
    assert is_deleted is True

    with pytest.raises(ValueError, match="not found"):
        await get_user(session, user.id)


@pytest.mark.asyncio
async def test_delete_non_existent_user(session):
    is_deleted = await delete_user(session, 9999)
    assert is_deleted is False


@pytest.mark.asyncio
async def test_get_all_users(session):
    for i in range(10):
        await create_user(
            session,
            UserCreate(
                email=f"user_{i}@mail.com",
                password="test",
                full_name=f"User {i}",
            ),
        )

    page = await get_all_users(session, offset=0, limit=2)
    assert len(page) == 2

    offset_page = await get_all_users(session, offset=5, limit=100)
    assert len(offset_page) == 5


@pytest.mark.asyncio
async def test_create_duplicate_email(session):
    user_data = UserCreate(
        email="duplicate@mail.com",
        password="test",
        full_name="Test User",
    )
    await create_user(session, user_data)

    with pytest.raises(Exception):
        await create_user(session, user_data)
        await session.flush()
