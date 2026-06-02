from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.services.user import authenticate_user, register_user


def _user(username: str = "alice", password: str = "secret") -> Mock:
    from app.services.auth import hash_password

    user = Mock()
    user.username = username
    user.hashed_password = hash_password(password)
    return user


async def test_register_user_success():
    repo = Mock()
    repo.get_by_username = AsyncMock(return_value=None)
    repo.create = AsyncMock()

    await register_user(repo, "newuser", "password123")

    repo.create.assert_awaited_once()
    assert repo.create.await_args.args[0] == "newuser"


async def test_register_user_existing_username_rejected():
    repo = Mock()
    repo.get_by_username = AsyncMock(return_value=_user())
    repo.create = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await register_user(repo, "alice", "password123")

    assert exc.value.status_code == status.HTTP_409_CONFLICT
    repo.create.assert_not_awaited()


async def test_register_user_integrity_error_maps_to_conflict():
    """A race that slips past the pre-check surfaces as IntegrityError -> 409."""
    repo = Mock()
    repo.get_by_username = AsyncMock(return_value=None)
    repo.create = AsyncMock(side_effect=IntegrityError("stmt", {}, Exception("dup")))

    with pytest.raises(HTTPException) as exc:
        await register_user(repo, "alice", "password123")

    assert exc.value.status_code == status.HTTP_409_CONFLICT


async def test_authenticate_user_success():
    repo = Mock()
    repo.get_by_username = AsyncMock(return_value=_user("bob", "correct"))

    assert await authenticate_user(repo, "bob", "correct") == "bob"


async def test_authenticate_user_unknown_user_rejected():
    repo = Mock()
    repo.get_by_username = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await authenticate_user(repo, "ghost", "whatever")

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


async def test_authenticate_user_wrong_password_rejected():
    repo = Mock()
    repo.get_by_username = AsyncMock(return_value=_user("bob", "correct"))

    with pytest.raises(HTTPException) as exc:
        await authenticate_user(repo, "bob", "wrong")

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
