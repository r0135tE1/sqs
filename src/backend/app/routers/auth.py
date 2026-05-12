from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies import get_user_repo
from app.models.user import LoginRequest, RegisterRequest, TokenResponse
from app.repositories.user import UserRepository
from app.services import user as user_service
from app.services.auth import create_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account. Username must be unique.",
)
async def register(body: RegisterRequest, repo: Annotated[UserRepository, Depends(get_user_repo)]) -> dict:
    await user_service.register_user(repo, body.username, body.password)
    return {"message": "User created successfully."}


@router.post(
    "/login",
    summary="Login and receive a JWT",
    description=(
        "Authenticates a user and returns a signed JWT. "
        "Include the token as `Authorization: Bearer <token>` on protected endpoints."
    ),
)
async def login(body: LoginRequest, repo: Annotated[UserRepository, Depends(get_user_repo)]) -> TokenResponse:
    username = await user_service.authenticate_user(repo, body.username, body.password)
    return TokenResponse(access_token=create_token(username))
