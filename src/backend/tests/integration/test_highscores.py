from app.services.game_session import game_session_store


async def _register_and_login(client, username: str, password: str = "password123") -> str:
    await client.post("/auth/register", json={"username": username, "password": password})
    resp = await client.post("/auth/login", json={"username": username, "password": password})
    return resp.json()["access_token"]


async def _session_with_score(client, score: int) -> str:
    """Create a game session and play `score` correct answers via the game API."""
    resp = await client.post("/game/session")
    session_id = resp.json()["session_id"]
    for _ in range(score):
        flag_resp = await client.get("/game/flag", params={"session_id": session_id})
        if flag_resp.status_code != 200:
            break
        question_id = flag_resp.json()["question_id"]
        correct = game_session_store._questions[question_id].correct_answer
        await client.post(
            "/game/answer",
            json={"question_id": question_id, "answer": correct},
        )
    return session_id


async def test_get_highscores_authenticated(async_client):
    token = await _register_and_login(async_client, "hs_user1")
    response = await async_client.get(
        "/highscores/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_get_highscores_no_token(async_client):
    response = await async_client.get("/highscores/")
    assert response.status_code == 401


async def test_get_highscores_invalid_token(async_client):
    response = await async_client.get(
        "/highscores/", headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


async def test_save_score_authenticated(async_client):
    token = await _register_and_login(async_client, "scorer1")
    session_id = await _session_with_score(async_client, 3)
    response = await async_client.post(
        "/highscores/",
        json={"session_id": session_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201


async def test_save_score_no_token(async_client):
    session_id = await _session_with_score(async_client, 1)
    response = await async_client.post("/highscores/", json={"session_id": session_id})
    assert response.status_code == 401


async def test_save_score_unknown_session(async_client):
    token = await _register_and_login(async_client, "scorer_invalid")
    response = await async_client.post(
        "/highscores/",
        json={"session_id": "00000000-0000-0000-0000-000000000000"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


async def test_arbitrary_score_rejected(async_client):
    """Clients must not be able to submit an arbitrary score value."""
    token = await _register_and_login(async_client, "cheater")
    response = await async_client.post(
        "/highscores/",
        json={"score": 99999},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


async def test_save_score_updates_when_new_personal_best(async_client):
    token = await _register_and_login(async_client, "updater")
    session_id = await _session_with_score(async_client, 2)
    await async_client.post(
        "/highscores/",
        json={"session_id": session_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    session_id2 = await _session_with_score(async_client, 5)
    response = await async_client.post(
        "/highscores/",
        json={"session_id": session_id2},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["message"] == "Score saved."


async def test_save_score_not_new_personal_best(async_client):
    token = await _register_and_login(async_client, "no_pb")
    session_id = await _session_with_score(async_client, 5)
    await async_client.post(
        "/highscores/",
        json={"session_id": session_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    session_id2 = await _session_with_score(async_client, 2)
    response = await async_client.post(
        "/highscores/",
        json={"session_id": session_id2},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["message"] == "Score not a new personal best."


async def test_highscores_ordered_by_score_desc(async_client):
    for username, score in [("leader_high", 5), ("leader_low", 2)]:
        token = await _register_and_login(async_client, username)
        session_id = await _session_with_score(async_client, score)
        await async_client.post(
            "/highscores/",
            json={"session_id": session_id},
            headers={"Authorization": f"Bearer {token}"},
        )

    token = await _register_and_login(async_client, "leader_viewer")
    response = await async_client.get(
        "/highscores/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    scores = [entry["score"] for entry in response.json()]
    assert scores == sorted(scores, reverse=True)
