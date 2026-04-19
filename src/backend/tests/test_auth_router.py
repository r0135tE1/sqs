import pytest
from httpx import AsyncClient


async def test_register_success(client: AsyncClient):
    resp = await client.post("/auth/register", json={"username": "alice", "password": "password1"})
    assert resp.status_code == 201
    assert resp.json()["message"] == "User created successfully."


async def test_register_duplicate_username(client: AsyncClient):
    await client.post("/auth/register", json={"username": "bob", "password": "password1"})
    resp = await client.post("/auth/register", json={"username": "bob", "password": "password1"})
    assert resp.status_code == 409


async def test_register_username_too_short(client: AsyncClient):
    resp = await client.post("/auth/register", json={"username": "ab", "password": "password1"})
    assert resp.status_code == 422


async def test_register_password_too_short(client: AsyncClient):
    resp = await client.post("/auth/register", json={"username": "validuser", "password": "short"})
    assert resp.status_code == 422


async def test_login_success(client: AsyncClient):
    await client.post("/auth/register", json={"username": "carol", "password": "password1"})
    resp = await client.post("/auth/login", json={"username": "carol", "password": "password1"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    await client.post("/auth/register", json={"username": "dave", "password": "password1"})
    resp = await client.post("/auth/login", json={"username": "dave", "password": "wrongpass"})
    assert resp.status_code == 401


async def test_login_unknown_user(client: AsyncClient):
    resp = await client.post("/auth/login", json={"username": "nobody", "password": "password1"})
    assert resp.status_code == 401
