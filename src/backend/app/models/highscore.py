from pydantic import BaseModel, Field


class HighscoreEntry(BaseModel):
    username: str
    score: int


class SaveScoreRequest(BaseModel):
    score: int = Field(ge=0)
