import logging

from pydantic_settings import BaseSettings

#Central Config-Values from .env or default values
class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/funwithflags"
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    restcountries_url: str = "https://restcountries.com/v3.1"
    cors_origins: list[str] = ["http://localhost:5173"]
    log_level: str = "INFO"

    model_config = {"env_file": ".env"}


settings = Settings()

logging.basicConfig(
    level=settings.log_level,
    format="%(levelname)s [%(name)s] %(message)s",
)
