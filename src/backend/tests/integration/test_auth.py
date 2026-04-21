async def test_register_success(async_client):
    response = await async_client.post(
        "/auth/register", json={"username": "alice", "password": "password123"}
    )
    assert response.status_code == 201
    assert "message" in response.json()


async def test_register_duplicate_username(async_client):
    await async_client.post(
        "/auth/register", json={"username": "bob", "password": "password123"}
    )
    response = await async_client.post(
        "/auth/register", json={"username": "bob", "password": "password123"}
    )
    assert response.status_code == 409


async def test_login_success(async_client):
    await async_client.post(
        "/auth/register", json={"username": "carol", "password": "password123"}
    )
    response = await async_client.post(
        "/auth/login", json={"username": "carol", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_wrong_password(async_client):
    await async_client.post(
        "/auth/register", json={"username": "dave", "password": "password123"}
    )
    response = await async_client.post(
        "/auth/login", json={"username": "dave", "password": "wrongpass123"}
    )
    assert response.status_code == 401


async def test_login_unknown_user(async_client):
    response = await async_client.post(
        "/auth/login", json={"username": "nobody", "password": "password123"}
    )
    assert response.status_code == 401
