from unittest.mock import AsyncMock, patch

import httpx

from app.services.game_session import game_session_store


async def _create_session(client) -> str:
    resp = await client.post("/game/session")
    assert resp.status_code == 201
    return resp.json()["session_id"]


async def _get_flag(client, session_id: str):
    resp = await client.get("/game/flag", params={"session_id": session_id})
    assert resp.status_code == 200
    return resp.json()


async def _answer(client, question_id: str, answer: str):
    return await client.post(
        "/game/answer",
        json={"question_id": question_id, "answer": answer},
    )


async def test_create_session_returns_session_id(async_client):
    resp = await async_client.post("/game/session")
    assert resp.status_code == 201
    assert "session_id" in resp.json()


async def test_get_flag_returns_correct_fields(async_client):
    sid = await _create_session(async_client)
    flag = await _get_flag(async_client, sid)
    assert set(flag.keys()) == {"question_id", "flag_url", "options"}


async def test_get_flag_no_correct_answer_in_response(async_client):
    """country_name must never be sent to the client."""
    sid = await _create_session(async_client)
    flag = await _get_flag(async_client, sid)
    assert "country_name" not in flag


async def test_get_flag_url_is_proxy_not_cdn(async_client):
    """flag_url must point to the backend proxy, not the CDN."""
    sid = await _create_session(async_client)
    flag = await _get_flag(async_client, sid)
    qid = flag["question_id"]
    assert flag["flag_url"] == f"/game/image/{qid}"
    assert "flagcdn" not in flag["flag_url"]


async def test_get_flag_has_four_options(async_client):
    sid = await _create_session(async_client)
    flag = await _get_flag(async_client, sid)
    assert len(flag["options"]) == 4


async def test_get_flag_unknown_session(async_client):
    resp = await async_client.get("/game/flag", params={"session_id": "invalid-session"})
    assert resp.status_code == 404


async def test_answer_correct(async_client):
    sid = await _create_session(async_client)
    flag = await _get_flag(async_client, sid)
    qid = flag["question_id"]
    correct = game_session_store._questions[qid].correct_answer

    resp = await _answer(async_client, qid, correct)
    assert resp.status_code == 200
    body = resp.json()
    assert body["correct"] is True
    assert body["score"] == 1
    assert body["correct_answer"] == correct


async def test_answer_wrong(async_client):
    sid = await _create_session(async_client)
    flag = await _get_flag(async_client, sid)
    qid = flag["question_id"]

    resp = await _answer(async_client, qid, "DEFINITELY WRONG")
    assert resp.status_code == 200
    body = resp.json()
    assert body["correct"] is False
    assert body["score"] == 0


async def test_answer_invalid_question_id(async_client):
    sid = await _create_session(async_client)
    resp = await _answer(async_client, "00000000-0000-0000-0000-000000000000", "Germany")
    assert resp.status_code == 400


async def test_answer_question_can_only_be_used_once(async_client):
    sid = await _create_session(async_client)
    flag = await _get_flag(async_client, sid)
    qid = flag["question_id"]

    await _answer(async_client, qid, "WRONG")
    # Second submission with the same question_id must fail
    resp = await _answer(async_client, qid, "WRONG")
    assert resp.status_code == 400


async def test_score_increments_on_consecutive_correct_answers(async_client):
    sid = await _create_session(async_client)
    for expected in range(1, 4):
        flag = await _get_flag(async_client, sid)
        qid = flag["question_id"]
        correct = game_session_store._questions[qid].correct_answer
        resp = await _answer(async_client, qid, correct)
        assert resp.json()["score"] == expected


async def test_score_resets_on_wrong_answer(async_client):
    sid = await _create_session(async_client)
    for _ in range(3):
        flag = await _get_flag(async_client, sid)
        qid = flag["question_id"]
        correct = game_session_store._questions[qid].correct_answer
        await _answer(async_client, qid, correct)

    flag = await _get_flag(async_client, sid)
    resp = await _answer(async_client, flag["question_id"], "WRONG")
    assert resp.json()["score"] == 0


async def test_seen_flags_not_repeated(async_client):
    sid = await _create_session(async_client)
    seen_urls = set()
    for _ in range(5):
        flag = await _get_flag(async_client, sid)
        url = flag["flag_url"]
        assert url not in seen_urls, f"Flag {url} shown twice"
        seen_urls.add(url)
        qid = flag["question_id"]
        correct = game_session_store._questions[qid].correct_answer
        await _answer(async_client, qid, correct)


async def test_image_proxy_returns_image(async_client):
    sid = await _create_session(async_client)
    flag = await _get_flag(async_client, sid)
    proxy_path = flag["flag_url"]

    fake_image = b"<svg>fake</svg>"
    mock_response = httpx.Response(200, content=fake_image, headers={"content-type": "image/svg+xml"})
    mock_response.request = httpx.Request("GET", "https://flagcdn.com/test.svg")

    with patch("app.routers.game.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        resp = await async_client.get(proxy_path)

    assert resp.status_code == 200
    assert resp.content == fake_image
    assert resp.headers["content-type"] == "image/svg+xml"


async def test_image_proxy_hides_cdn_url(async_client):
    """The client must never see the real CDN URL in any response field."""
    sid = await _create_session(async_client)
    flag = await _get_flag(async_client, sid)
    assert "flagcdn" not in flag["flag_url"]
    assert "restcountries" not in flag["flag_url"]


async def test_image_proxy_unknown_question_returns_404(async_client):
    resp = await async_client.get("/game/image/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


async def test_all_flags_shown_returns_404(async_client):
    sid = await _create_session(async_client)
    for _ in range(10):
        flag_resp = await async_client.get("/game/flag", params={"session_id": sid})
        if flag_resp.status_code == 404:
            return
        qid = flag_resp.json()["question_id"]
        correct = game_session_store._questions[qid].correct_answer
        await _answer(async_client, qid, correct)

    resp = await async_client.get("/game/flag", params={"session_id": sid})
    assert resp.status_code == 404
