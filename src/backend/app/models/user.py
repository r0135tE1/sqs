from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def password_not_blank(cls, v: str) -> str:
        # Check if the password is not blank / is containing space 8 times
        if not v.strip():
            raise ValueError("Password must not be blank.")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
