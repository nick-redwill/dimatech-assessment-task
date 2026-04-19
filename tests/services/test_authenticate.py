import pytest

from schemas.user import UserCreate
from repo.user import create_user

from services.user import authenticate_user
from utils.auth import decode_jwt
from exceptions import AuthError


@pytest.mark.asyncio
async def test_authenticate_user_success(session):
    await create_user(
        session,
        UserCreate(
            email="test@mail.com", password="testpass", full_name="Test User"
        ),
    )
    token = await authenticate_user(session, "test@mail.com", "testpass")
    payload = decode_jwt(token)
    assert payload["sub"] is not None
    assert payload["role"] == "user"


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(session):
    await create_user(
        session,
        UserCreate(
            email="test@mail.com", password="testpass", full_name="Test User"
        ),
    )
    with pytest.raises(AuthError):
        await authenticate_user(session, "test@mail.com", "wrongpass")


@pytest.mark.asyncio
async def test_authenticate_user_nonexistent_email(session):
    with pytest.raises(AuthError):
        await authenticate_user(session, "ghost@mail.com", "testpass")
