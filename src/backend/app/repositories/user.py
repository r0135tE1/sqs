from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str) -> User | None:
        return await self.db.scalar(select(User).where(User.username == username))

    async def create(self, username: str, hashed_password: str) -> None:
        self.db.add(User(username=username, hashed_password=hashed_password))
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
