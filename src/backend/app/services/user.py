from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models import User
from app.services.auth import hash_password, verify_password


async def register_user(db: AsyncSession, username: str, password: str) -> None:
    existing = await db.scalar(select(User).where(User.username == username))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken.")

    user = User(username=username, hashed_password=hash_password(password))
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken.")


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User:
    user = await db.scalar(select(User).where(User.username == username))
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    return user
