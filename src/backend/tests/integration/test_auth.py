_PASS = "test-pass-1"
_WRONG_PASS = "test-wrong-pass"


async def test_register_success(async_client):
    response = await async_client.post(
        "/auth/register", json={"username": "alice", "password": _PASS}
    )
    assert response.status_code == 201
    assert "message" in response.json()


async def test_register_duplicate_username(async_client):
    await async_client.post(
        "/auth/register", json={"username": "bob", "password": _PASS}
    )
    response = await async_client.post(
        "/auth/register", json={"username": "bob", "password": _PASS}
    )
    assert response.status_code == 409


async def test_login_success(async_client):
    await async_client.post(
        "/auth/register", json={"username": "carol", "password": _PASS}
    )
    response = await async_client.post(
        "/auth/login", json={"username": "carol", "password": _PASS}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_wrong_password(async_client):
    await async_client.post(
        "/auth/register", json={"username": "dave", "password": _PASS}
    )
    response = await async_client.post(
        "/auth/login", json={"username": "dave", "password": _WRONG_PASS}
    )
    assert response.status_code == 401


async def test_login_unknown_user(async_client):
    response = await async_client.post(
        "/auth/login", json={"username": "nobody", "password": _PASS}
    )
    assert response.status_code == 401
