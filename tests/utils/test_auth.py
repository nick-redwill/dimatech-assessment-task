import pytest
from datetime import timedelta
from jose import jwt
from settings import SECRET_KEY
from utils.auth import (
    hash_password,
    verify_password,
    create_jwt_token,
    decode_jwt,
)
from exceptions import AuthError


def test_hash_password_returns_hash():
    hashed = hash_password("mypassword")
    assert hashed != "mypassword"
    assert hashed.startswith("$argon2")


def test_verify_password_correct():
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("mypassword")
    assert verify_password("wrongpassword", hashed) is False


def test_hash_is_unique():
    assert hash_password("mypassword") != hash_password("mypassword")


def test_create_and_decode_jwt():
    token = create_jwt_token({"sub": "1", "role": "USER"})
    payload = decode_jwt(token)
    assert payload["sub"] == "1"
    assert payload["role"] == "USER"


def test_decode_jwt_expired():
    token = create_jwt_token({"sub": "1"}, expires_delta=timedelta(seconds=-1))
    with pytest.raises(AuthError, match="expired"):
        decode_jwt(token)


def test_decode_jwt_invalid():
    with pytest.raises(AuthError, match="Invalid"):
        decode_jwt("this.is.not.a.valid.token")


def test_decode_jwt_tampered():
    token = create_jwt_token({"sub": "1", "role": "USER"})
    tampered = token + "tampered"
    with pytest.raises(AuthError):
        decode_jwt(tampered)
