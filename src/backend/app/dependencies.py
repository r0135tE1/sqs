from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import get_db
from app.repositories.highscore import HighscoreRepository
from app.repositories.user import UserRepository
from app.services.auth import decode_token

bearer = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    username = decode_token(credentials.credentials)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return username


async def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


async def get_highscore_repo(db: AsyncSession = Depends(get_db)) -> HighscoreRepository:
    return HighscoreRepository(db)
