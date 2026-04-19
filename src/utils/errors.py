from functools import wraps
from sanic.exceptions import BadRequest, Forbidden, Unauthorized, NotFound
from exceptions import (
    AppError,
    DuplicateError,
    PermissionError,
    AuthError,
    NotFoundError,
)

EXCEPTION_MAP = {
    AppError: BadRequest,
    DuplicateError: BadRequest,
    AuthError: Unauthorized,
    PermissionError: Forbidden,
    NotFoundError: NotFound,
}


def handle_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):

        try:
            return await func(*args, **kwargs)
        except AppError as e:
            sanic_exc = EXCEPTION_MAP.get(type(e), BadRequest)
            raise sanic_exc(str(e))

    return wrapper
