from sanic.request import Request
from sanic.exceptions import Unauthorized, Forbidden

from utils.auth import decode_jwt
from enums import UserRole

from functools import wraps
from sanic.request import Request
from db import AsyncSessionLocal


def with_db_session(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        async with AsyncSessionLocal() as session:
            try:
                result = await func(
                    request, *args, db_session=session, **kwargs
                )
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise

    return wrapper


def get_current_user(request: Request) -> dict:
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    if not token:
        raise Unauthorized("Missing token")

    return decode_jwt(token)


def require_admin(request: Request) -> dict:
    payload = get_current_user(request)
    if payload.get("role") != UserRole.ADMIN.value:
        raise Forbidden("Admins only")

    return payload
