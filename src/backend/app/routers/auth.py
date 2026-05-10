from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_session import get_db
from app.models.user import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth import create_token
from app.services import user as user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account. Username must be unique.",
)
async def register(body: RegisterRequest, db: Annotated[AsyncSession, Depends(get_db)]) -> dict:
    await user_service.register_user(db, body.username, body.password)
    return {"message": "User created successfully."}


@router.post(
    "/login",
    summary="Login and receive a JWT",
    description=(
        "Authenticates a user and returns a signed JWT. "
        "Include the token as `Authorization: Bearer <token>` on protected endpoints."
    ),
)
async def login(body: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]) -> TokenResponse:
    user = await user_service.authenticate_user(db, body.username, body.password)
    return TokenResponse(access_token=create_token(user.username))
