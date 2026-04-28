from pydantic import BaseModel


class HighscoreEntry(BaseModel):
    username: str
    score: int


class SaveSessionRequest(BaseModel):
    session_id: str
