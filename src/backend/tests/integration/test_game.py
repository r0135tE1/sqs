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
    assert set(flag.keys()) == {"question_id", "flag_svg", "options"}


async def test_get_flag_no_correct_answer_in_response(async_client):
    """country_name must never be sent to the client."""
    sid = await _create_session(async_client)
    flag = await _get_flag(async_client, sid)
    assert "country_name" not in flag


async def test_get_flag_svg_is_valid(async_client):
    """flag_svg must contain SVG markup — no CDN URL ever reaches the client."""
    sid = await _create_session(async_client)
    flag = await _get_flag(async_client, sid)
    assert "<svg" in flag["flag_svg"]
    assert "flagcdn" not in flag["flag_svg"]


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
    correct = game_session_store.get_correct_answer(qid)

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
    await _create_session(async_client)
    resp = await _answer(async_client, "00000000-0000-0000-0000-000000000000", "Germany")
    assert resp.status_code == 400


async def test_answer_question_can_only_be_used_once(async_client):
    sid = await _create_session(async_client)
    flag = await _get_flag(async_client, sid)
    qid = flag["question_id"]

    await _answer(async_client, qid, "WRONG")
    resp = await _answer(async_client, qid, "WRONG")
    assert resp.status_code == 400


async def test_score_increments_on_consecutive_correct_answers(async_client):
    sid = await _create_session(async_client)
    for expected in range(1, 4):
        flag = await _get_flag(async_client, sid)
        qid = flag["question_id"]
        correct = game_session_store.get_correct_answer(qid)
        resp = await _answer(async_client, qid, correct)
        assert resp.json()["score"] == expected


async def test_score_resets_on_wrong_answer(async_client):
    sid = await _create_session(async_client)
    for _ in range(3):
        flag = await _get_flag(async_client, sid)
        qid = flag["question_id"]
        correct = game_session_store.get_correct_answer(qid)
        await _answer(async_client, qid, correct)

    flag = await _get_flag(async_client, sid)
    resp = await _answer(async_client, flag["question_id"], "WRONG")
    assert resp.json()["score"] == 0


async def test_seen_flags_not_repeated(async_client):
    sid = await _create_session(async_client)
    seen_svgs = set()
    for _ in range(5):
        flag = await _get_flag(async_client, sid)
        svg = flag["flag_svg"]
        assert svg not in seen_svgs, "Same flag shown twice"
        seen_svgs.add(svg)
        qid = flag["question_id"]
        correct = game_session_store.get_correct_answer(qid)
        await _answer(async_client, qid, correct)


async def test_all_flags_shown_returns_410(async_client):
    sid = await _create_session(async_client)
    for _ in range(10):
        flag_resp = await async_client.get("/game/flag", params={"session_id": sid})
        if flag_resp.status_code == 410:
            return
        qid = flag_resp.json()["question_id"]
        correct = game_session_store.get_correct_answer(qid)
        await _answer(async_client, qid, correct)

    resp = await async_client.get("/game/flag", params={"session_id": sid})
    assert resp.status_code == 410
