from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.config import settings
from app.services.auth import create_token, decode_token, hash_password, verify_password


def test_hash_and_verify_password():
    hashed = hash_password("mysecret123")
    assert verify_password("mysecret123", hashed)


def test_wrong_password_rejected():
    hashed = hash_password("correctpassword")
    assert not verify_password("wrongpassword", hashed)


def test_create_token_contains_sub():
    token = create_token("alice")
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    assert payload["sub"] == "alice"


def test_create_token_expiry():
    before = datetime.now(timezone.utc)
    token = create_token("alice")
    after = datetime.now(timezone.utc)

    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

    expected_min = before + timedelta(minutes=settings.jwt_expire_minutes - 1)
    expected_max = after + timedelta(minutes=settings.jwt_expire_minutes + 1)
    assert expected_min <= exp <= expected_max


def test_decode_valid_token():
    token = create_token("bob")
    assert decode_token(token) == "bob"


def test_decode_expired_token():
    expired = jwt.encode(
        {"sub": "alice", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    assert decode_token(expired) is None


def test_decode_tampered_token():
    token = create_token("alice")
    tampered = token[:-5] + "XXXXX"
    assert decode_token(tampered) is None


def test_decode_garbage_string():
    assert decode_token("not.a.jwt.token") is None
