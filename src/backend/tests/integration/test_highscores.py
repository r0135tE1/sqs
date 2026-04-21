async def _register_and_login(client, username: str, password: str = "password123") -> str:
    await client.post("/auth/register", json={"username": username, "password": password})
    resp = await client.post("/auth/login", json={"username": username, "password": password})
    return resp.json()["access_token"]


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
    response = await async_client.post(
        "/highscores/",
        json={"score": 42},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201


async def test_save_score_no_token(async_client):
    response = await async_client.post("/highscores/", json={"score": 10})
    assert response.status_code == 401


async def test_highscores_ordered_by_score_desc(async_client):
    for username, score in [("leader_high", 100), ("leader_low", 10)]:
        token = await _register_and_login(async_client, username)
        await async_client.post(
            "/highscores/",
            json={"score": score},
            headers={"Authorization": f"Bearer {token}"},
        )

    token = await _register_and_login(async_client, "leader_viewer")
    response = await async_client.get(
        "/highscores/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    scores = [entry["score"] for entry in response.json()]
    assert scores == sorted(scores, reverse=True)
