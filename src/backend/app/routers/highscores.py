from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user, get_highscore_repo, get_user_repo
from app.models.highscore import HighscoreEntry, SaveSessionRequest
from app.repositories.highscore import HighscoreRepository
from app.repositories.user import UserRepository
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
    hs_repo: Annotated[HighscoreRepository, Depends(get_highscore_repo)],
) -> list[HighscoreEntry]:
    return await highscore_service.get_top_highscores(hs_repo)


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
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    hs_repo: Annotated[HighscoreRepository, Depends(get_highscore_repo)],
) -> dict:
    score = game_session_store.get_best_score(body.session_id)
    if score is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    result = await highscore_service.save_score(user_repo, hs_repo, current_user, score)
    game_session_store.delete_session(body.session_id)
    return result
