from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

#define DB connection
engine = create_async_engine(settings.database_url, echo=False)

#define db session
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

#create and provide db session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
