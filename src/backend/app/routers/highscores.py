from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import get_db
from app.database.models import Highscore, User
from app.dependencies import get_current_user
from app.models.highscore import HighscoreEntry, SaveSessionRequest
from app.services.game_session import game_session_store

router = APIRouter(prefix="/highscores", tags=["highscores"])


@router.get(
    "/",
    summary="Get top highscores (protected)",
    description=(
        "Returns the top 10 highscores across all users, sorted by score descending. "
        "Requires a valid JWT in the `Authorization: Bearer <token>` header."
    ),
)
async def get_highscores(
    current_user: Annotated[str, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[HighscoreEntry]:
    rows = await db.execute(
        select(User.username, Highscore.score)
        .join(User, Highscore.user_id == User.id)
        .order_by(Highscore.score.desc())
        .limit(10)
    )
    return [HighscoreEntry(username=row.username, score=row.score) for row in rows]


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Save highscore for a game session (protected)",
    description=(
        "Saves the authenticated user's best streak from the given game session. "
        "The score is read from the server-side session — the client cannot submit "
        "an arbitrary value."
    ),
)
async def save_score(
    body: SaveSessionRequest,
    current_user: Annotated[str, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    score = game_session_store.get_best_score(body.session_id)
    if score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )

    user = await db.scalar(select(User).where(User.username == current_user))
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
