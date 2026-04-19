import os
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing-only")

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database.engine import get_db
from app.database.models import Base
from app.services.flag_cache import flag_cache
from main import app

_TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

_TEST_COUNTRIES = [
    {"name": "Germany", "flag_url": "https://flagcdn.com/de.svg", "code": "DE"},
    {"name": "France",  "flag_url": "https://flagcdn.com/fr.svg", "code": "FR"},
    {"name": "Spain",   "flag_url": "https://flagcdn.com/es.svg", "code": "ES"},
    {"name": "Italy",   "flag_url": "https://flagcdn.com/it.svg", "code": "IT"},
]


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(_TEST_DB_URL, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_engine):
    factory = async_sessionmaker(db_engine, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    flag_cache._countries = list(_TEST_COUNTRIES)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


async def register_and_login(client: AsyncClient, username: str = "testuser", password: str = "testpass1") -> str:
    await client.post("/auth/register", json={"username": username, "password": password})
    resp = await client.post("/auth/login", json={"username": username, "password": password})
    return resp.json()["access_token"]
