from jose import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from datetime import datetime, timezone, timedelta
from settings import SECRET_KEY

ph = PasswordHasher()


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False


def create_jwt_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=60)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY)
