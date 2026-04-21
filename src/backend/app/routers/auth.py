from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import get_db
from app.database.models import User
from app.models.user import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth import create_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

#User Registration with Duplicate Usernames check and db save
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account. Username must be unique.",
)
async def register( body: RegisterRequest, db: Annotated[AsyncSession, Depends(get_db)] ) -> dict:
    existing = await db.scalar(select(User).where(User.username == body.username))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken.")

    user = User(username=body.username, hashed_password=hash_password(body.password))
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken.")
    return {"message": "User created successfully."}

#User Login with JSON Web Token generation
@router.post(
    "/login",
    summary="Login and receive a JWT",
    description=(
        "Authenticates a user and returns a signed JWT. "
        "Include the token as `Authorization: Bearer <token>` on protected endpoints."
    ),
)
async def login(body: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)] ) -> TokenResponse:
    user = await db.scalar(select(User).where(User.username == body.username))
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    return TokenResponse(access_token=create_token(user.username))
