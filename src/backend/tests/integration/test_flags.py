from app.services.flag_cache import flag_cache


async def test_random_flag_ok(async_client):
    response = await async_client.get("/flags/random")
    assert response.status_code == 200
    body = response.json()
    assert {"country_code", "country_name", "flag_url", "options"} == set(body.keys())


async def test_random_flag_options_count(async_client):
    response = await async_client.get("/flags/random")
    assert response.status_code == 200
    assert len(response.json()["options"]) == 4


async def test_random_flag_exclude_all(async_client):
    all_codes = [f"C{i}" for i in range(10)]
    params = [("exclude", code) for code in all_codes]
    response = await async_client.get("/flags/random", params=params)
    assert response.status_code == 404


async def test_random_flag_empty_cache(async_client):
    original = list(flag_cache._countries)
    flag_cache._countries = []
    try:
        response = await async_client.get("/flags/random")
        assert response.status_code == 404
    finally:
        flag_cache._countries = original
