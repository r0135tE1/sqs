from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt

from app.config import settings
from app.dependencies import get_current_user
from app.services.auth import create_token


def test_get_current_user_valid_token():
    token = create_token("alice")
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    assert get_current_user(credentials=creds) == "alice"


def test_get_current_user_invalid_token():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token.here")
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=creds)
    assert exc_info.value.status_code == 401


def test_get_current_user_expired_token():
    expired = jwt.encode(
        {"sub": "alice", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=expired)
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=creds)
    assert exc_info.value.status_code == 401
