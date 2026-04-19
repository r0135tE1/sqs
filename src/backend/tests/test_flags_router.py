from httpx import AsyncClient


async def test_get_random_flag(client: AsyncClient):
    resp = await client.get("/flags/random")
    assert resp.status_code == 200
    data = resp.json()
    assert "country_code" in data
    assert "country_name" in data
    assert "flag_url" in data
    assert "options" in data
    assert len(data["options"]) == 4
    assert data["country_name"] in data["options"]


async def test_get_random_flag_excludes_seen(client: AsyncClient):
    resp = await client.get("/flags/random?exclude=DE&exclude=FR&exclude=ES&exclude=IT")
    assert resp.status_code == 404


async def test_get_random_flag_partial_exclude(client: AsyncClient):
    resp = await client.get("/flags/random?exclude=DE")
    assert resp.status_code == 200
    assert resp.json()["country_code"] != "DE"


async def test_health_check(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert resp.json()["flags_cached"] == 4
