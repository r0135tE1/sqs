from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Highscore, User
from app.models.highscore import HighscoreEntry


async def get_top_highscores(db: AsyncSession) -> list[HighscoreEntry]:
    rows = await db.execute(
        select(User.username, Highscore.score)
        .join(User, Highscore.user_id == User.id)
        .order_by(Highscore.score.desc())
        .limit(10)
    )
    return [HighscoreEntry(username=row.username, score=row.score) for row in rows]


async def save_score(db: AsyncSession, username: str, score: int) -> dict:
    user = await db.scalar(select(User).where(User.username == username))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    existing = await db.scalar(select(Highscore).where(Highscore.user_id == user.id))
    if existing is None:
        db.add(Highscore(user_id=user.id, score=score))
    elif score > existing.score:
        existing.score = score
    else:
        return {"message": "Score not a new personal best."}

    await db.commit()
    return {"message": "Score saved."}