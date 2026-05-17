"""
Security / Penetration Tests

Verifies that all protected endpoints and input validators reject malicious
or malformed input. These tests map directly to the SQS checklist requirement:
"Penetrations Tests: Tests die eure abgesicherten Endpunkte testen."
"""
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config import settings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _register_and_login(client, username: str, password: str = "validpass123") -> str:
    await client.post("/auth/register", json={"username": username, "password": password})
    resp = await client.post("/auth/login", json={"username": username, "password": password})
    return resp.json()["access_token"]


def _expired_token(username: str) -> str:
    return jwt.encode(
        {"sub": username, "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


# ---------------------------------------------------------------------------
# 1. Input Validation
# ---------------------------------------------------------------------------

async def test_sql_injection_in_username_rejected(async_client):
    response = await async_client.post(
        "/auth/register",
        json={"username": "'; DROP TABLE users;--", "password": "validpass123"},
    )
    assert response.status_code == 422


async def test_xss_payload_in_username_rejected(async_client):
    response = await async_client.post(
        "/auth/register",
        json={"username": "<script>alert(1)</script>", "password": "validpass123"},
    )
    assert response.status_code == 422


async def test_oversized_username_rejected(async_client):
    response = await async_client.post(
        "/auth/register",
        json={"username": "a" * 51, "password": "validpass123"},
    )
    assert response.status_code == 422


async def test_blank_password_rejected(async_client):
    response = await async_client.post(
        "/auth/register",
        json={"username": "validuser", "password": "        "},
    )
    assert response.status_code == 422


async def test_too_short_password_rejected(async_client):
    response = await async_client.post(
        "/auth/register",
        json={"username": "validuser", "password": "short"},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# 2. Auth Bypass — protected endpoints reject invalid tokens
# ---------------------------------------------------------------------------

async def test_no_token_get_highscores_rejected(async_client):
    response = await async_client.get("/highscores/")
    assert response.status_code == 401


async def test_no_token_post_highscores_rejected(async_client):
    response = await async_client.post("/highscores/", json={"session_id": "any"})
    assert response.status_code == 401


async def test_forged_jwt_rejected(async_client):
    response = await async_client.get(
        "/highscores/",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.forged.payload"},
    )
    assert response.status_code == 401


async def test_expired_jwt_rejected(async_client):
    token = _expired_token("someuser")
    response = await async_client.get(
        "/highscores/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


async def test_jwt_wrong_secret_rejected(async_client):
    token = jwt.encode(
        {"sub": "someuser", "exp": datetime.now(timezone.utc) + timedelta(minutes=30)},
        "wrong-secret",
        algorithm=settings.jwt_algorithm,
    )
    response = await async_client.get(
        "/highscores/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


async def test_garbage_token_rejected(async_client):
    response = await async_client.get(
        "/highscores/",
        headers={"Authorization": "Bearer not.a.real.token"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# 3. Score Manipulation
# ---------------------------------------------------------------------------

async def test_arbitrary_score_in_body_rejected(async_client):
    token = await _register_and_login(async_client, "sec_score_user")
    response = await async_client.post(
        "/highscores/",
        json={"score": 99999999},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


async def test_nonexistent_session_rejected(async_client):
    token = await _register_and_login(async_client, "sec_session_user")
    response = await async_client.post(
        "/highscores/",
        json={"session_id": "00000000-0000-0000-0000-000000000000"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404