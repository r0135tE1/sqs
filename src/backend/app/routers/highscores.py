from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import get_db
from app.database.models import Highscore, User
from app.dependencies import get_current_user
from app.models.highscore import HighscoreEntry, SaveScoreRequest

router = APIRouter(prefix="/highscores", tags=["highscores"])

#Get Highscore (only logged in Users)
@router.get(
    "/",
    summary="Get top highscores (protected)",
    description=(
        "Returns the top 10 highscores across all users, sorted by score descending. "
        "Requires a valid JWT in the `Authorization: Bearer <token>` header."
    ),
)
async def get_highscores(current_user: Annotated[str, Depends(get_current_user)],db: Annotated[AsyncSession, Depends(get_db)]) -> list[HighscoreEntry]:
    rows = await db.execute(
        select(User.username, Highscore.score)
        .join(User, Highscore.user_id == User.id)
        .order_by(Highscore.score.desc())
        .limit(10)
    )
    return [HighscoreEntry(username=row.username, score=row.score) for row in rows]

#Save Highscores (only logged in Users)
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Save a highscore (protected)",
    description=(
        "Saves the authenticated user's streak score to the database. "
        "Called at the end of a game session when the player is logged in."
    ),
)
async def save_score(body: SaveScoreRequest, current_user: Annotated[str, Depends(get_current_user)],db: Annotated[AsyncSession, Depends(get_db)] ) -> dict:
    user = await db.scalar(select(User).where(User.username == current_user))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    db.add(Highscore(user_id=user.id, score=body.score))
    await db.commit()
    return {"message": "Score saved."}
