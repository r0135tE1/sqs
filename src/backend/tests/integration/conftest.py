import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.engine.url import make_url
from testcontainers.postgres import PostgresContainer

from app.database.models import Base
from app.database.engine import get_db
from app.services.flag_cache import flag_cache


@pytest.fixture(scope="session")
def pg_container():
    with PostgresContainer("postgres:16") as container:
        yield container


@pytest.fixture(scope="session")
def db_async_url(pg_container):
    # Return a URL object (not str) — str(URL) in SQLAlchemy 2.x hides the password with *** which causes asyncpg auth failures.
    raw = pg_container.get_connection_url()
    return make_url(raw).set(drivername="postgresql+asyncpg")


@pytest_asyncio.fixture
async def async_client(db_async_url, seeded_flag_cache):
    from main import app

    engine = create_async_engine(db_async_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with AsyncSession(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with patch.object(flag_cache, "load", new_callable=AsyncMock):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    app.dependency_overrides.clear()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()
