from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.repositories.user import UserRepository
from app.services.auth import hash_password, verify_password

# Register User with exception saves against race conditions
async def register_user(repo: UserRepository, username: str, password: str) -> None:
    if await repo.get_by_username(username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken.")
    try:
        await repo.create(username, hash_password(password))
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken.")


async def authenticate_user(repo: UserRepository, username: str, password: str) -> str:
    user = await repo.get_by_username(username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    return user.username
