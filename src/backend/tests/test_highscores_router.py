from httpx import AsyncClient

from tests.conftest import register_and_login


async def test_get_highscores_requires_auth(client: AsyncClient):
    resp = await client.get("/highscores/")
    assert resp.status_code == 403


async def test_get_highscores_empty(client: AsyncClient):
    token = await register_and_login(client, "user1", "password1")
    resp = await client.get("/highscores/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


async def test_save_score(client: AsyncClient):
    token = await register_and_login(client, "user2", "password1")
    resp = await client.post(
        "/highscores/",
        json={"score": 10},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["message"] == "Score saved."


async def test_save_score_appears_in_list(client: AsyncClient):
    token = await register_and_login(client, "user3", "password1")
    await client.post("/highscores/", json={"score": 5}, headers={"Authorization": f"Bearer {token}"})
    resp = await client.get("/highscores/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    scores = resp.json()
    assert any(e["username"] == "user3" and e["score"] == 5 for e in scores)


async def test_save_score_updates_if_higher(client: AsyncClient):
    token = await register_and_login(client, "user4", "password1")
    headers = {"Authorization": f"Bearer {token}"}
    await client.post("/highscores/", json={"score": 5}, headers=headers)
    await client.post("/highscores/", json={"score": 15}, headers=headers)
    resp = await client.get("/highscores/", headers=headers)
    entry = next(e for e in resp.json() if e["username"] == "user4")
    assert entry["score"] == 15


async def test_save_score_ignores_if_lower(client: AsyncClient):
    token = await register_and_login(client, "user5", "password1")
    headers = {"Authorization": f"Bearer {token}"}
    await client.post("/highscores/", json={"score": 20}, headers=headers)
    resp = await client.post("/highscores/", json={"score": 5}, headers=headers)
    assert resp.json()["message"] == "Score not a new personal best."
    entry = next(e for e in (await client.get("/highscores/", headers=headers)).json() if e["username"] == "user5")
    assert entry["score"] == 20


async def test_save_score_invalid_negative(client: AsyncClient):
    token = await register_and_login(client, "user6", "password1")
    resp = await client.post(
        "/highscores/",
        json={"score": -1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
