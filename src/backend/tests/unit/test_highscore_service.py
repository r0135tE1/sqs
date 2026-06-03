from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException, status

from app.services.highscore import (
    get_top_highscores,
    get_user_highscore,
    save_score,
)


def _row(username: str, score: int) -> Mock:
    row = Mock()
    row.username = username
    row.score = score
    return row


async def test_get_top_highscores_maps_rows_to_entries():
    repo = Mock()
    repo.get_top_10 = AsyncMock(return_value=[_row("alice", 9), _row("bob", 4)])

    result = await get_top_highscores(repo)

    assert [(e.username, e.score) for e in result] == [("alice", 9), ("bob", 4)]


async def test_get_top_highscores_empty():
    repo = Mock()
    repo.get_top_10 = AsyncMock(return_value=[])

    assert await get_top_highscores(repo) == []


async def test_get_user_highscore_success():
    user_repo = Mock()
    user_repo.get_by_username = AsyncMock(return_value=Mock(id=1))
    hs_repo = Mock()
    hs_repo.get_by_user_id = AsyncMock(return_value=Mock(score=7))

    entry = await get_user_highscore(user_repo, hs_repo, "alice")

    assert entry.username == "alice"
    assert entry.score == 7


async def test_get_user_highscore_unknown_user_404():
    user_repo = Mock()
    user_repo.get_by_username = AsyncMock(return_value=None)
    hs_repo = Mock()
    hs_repo.get_by_user_id = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await get_user_highscore(user_repo, hs_repo, "ghost")

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    hs_repo.get_by_user_id.assert_not_awaited()


async def test_get_user_highscore_no_score_404():
    user_repo = Mock()
    user_repo.get_by_username = AsyncMock(return_value=Mock(id=1))
    hs_repo = Mock()
    hs_repo.get_by_user_id = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await get_user_highscore(user_repo, hs_repo, "alice")

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


async def test_save_score_new_best():
    user_repo = Mock()
    user_repo.get_by_username = AsyncMock(return_value=Mock(id=1))
    hs_repo = Mock()
    hs_repo.upsert = AsyncMock(return_value=(12, True))

    result = await save_score(user_repo, hs_repo, "alice", 12)

    assert result.highscore == 12
    assert result.is_new_best is True


async def test_save_score_not_a_new_best():
    user_repo = Mock()
    user_repo.get_by_username = AsyncMock(return_value=Mock(id=1))
    hs_repo = Mock()
    hs_repo.upsert = AsyncMock(return_value=(20, False))

    result = await save_score(user_repo, hs_repo, "alice", 5)

    assert result.highscore == 20
    assert result.is_new_best is False


async def test_save_score_zero_best_returns_none_highscore():
    user_repo = Mock()
    user_repo.get_by_username = AsyncMock(return_value=Mock(id=1))
    hs_repo = Mock()
    hs_repo.upsert = AsyncMock(return_value=(0, False))

    result = await save_score(user_repo, hs_repo, "alice", 0)

    assert result.highscore is None
    assert result.is_new_best is False


async def test_save_score_unknown_user_404():
    user_repo = Mock()
    user_repo.get_by_username = AsyncMock(return_value=None)
    hs_repo = Mock()
    hs_repo.upsert = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await save_score(user_repo, hs_repo, "ghost", 5)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    hs_repo.upsert.assert_not_awaited()
