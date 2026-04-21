async def test_health_ok(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert "flags_cached" in body
    assert body["flags_cached"] == 10  # seeded with 10 fake countries via seeded_flag_cache
