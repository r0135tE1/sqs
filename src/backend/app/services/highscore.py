from fastapi import HTTPException, status

from app.models.highscore import HighscoreEntry
from app.repositories.highscore import HighscoreRepository
from app.repositories.user import UserRepository


async def get_top_highscores(repo: HighscoreRepository) -> list[HighscoreEntry]:
    rows = await repo.get_top_10()
    return [HighscoreEntry(username=row.username, score=row.score) for row in rows]


async def save_score(user_repo: UserRepository, hs_repo: HighscoreRepository, username: str, score: int) -> dict:
    user = await user_repo.get_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return await hs_repo.upsert(user.id, score)
