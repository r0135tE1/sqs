from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_session import get_db
from app.dependencies import get_current_user
from app.models.highscore import HighscoreEntry, SaveSessionRequest
from app.services import highscore as highscore_service
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
    return await highscore_service.get_top_highscores(db)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Save highscore for a game sessdie ion (protected)",
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return await highscore_service.save_score(db, current_user, score)
