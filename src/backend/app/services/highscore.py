from fastapi import HTTPException, status

from app.models.highscore import HighscoreEntry, SaveScoreResponse
from app.repositories.highscore import HighscoreRepository
from app.repositories.user import UserRepository


async def get_top_highscores(repo: HighscoreRepository) -> list[HighscoreEntry]:
    rows = await repo.get_top_10()
    return [HighscoreEntry(username=row.username, score=row.score) for row in rows]


async def get_user_highscore(user_repo: UserRepository, hs_repo: HighscoreRepository, username: str) -> HighscoreEntry:
    user = await user_repo.get_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    entry = await hs_repo.get_by_user_id(user.id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No highscore found for this user.")
    return HighscoreEntry(username=username, score=entry.score)


async def save_score(user_repo: UserRepository, hs_repo: HighscoreRepository, username: str, score: int) -> SaveScoreResponse:
    user = await user_repo.get_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    current_best, is_new_best = await hs_repo.upsert(user.id, score)
    return SaveScoreResponse(highscore=current_best, is_new_best=is_new_best)
