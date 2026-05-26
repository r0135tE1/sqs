from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Highscore, User


class HighscoreRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_top_10(self) -> list:
        result = await self.db.execute(
            select(User.username, Highscore.score)
            .join(User, Highscore.user_id == User.id)
            .order_by(Highscore.score.desc())
            .limit(10)
        )
        return result.all()

    async def get_by_user_id(self, user_id: int) -> Highscore | None:
        return await self.db.scalar(select(Highscore).where(Highscore.user_id == user_id))

    async def upsert(self, user_id: int, score: int) -> tuple[int, bool]:
        """Persist score if it beats the existing best. Returns (current_best, was_saved)."""
        existing = await self.get_by_user_id(user_id)
        existing_score = existing.score if existing else 0
        if score <= 0 or score <= existing_score:
            return existing_score, False
        if existing is None:
            self.db.add(Highscore(user_id=user_id, score=score))
        else:
            existing.score = score
        await self.db.commit()
        return score, True
