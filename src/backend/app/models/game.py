from pydantic import BaseModel


class SessionResponse(BaseModel):
    session_id: str


class FlagQuestion(BaseModel):
    question_id: str
    flag_svg: str
    options: list[str]


class AnswerRequest(BaseModel):
    question_id: str
    answer: str


class AnswerResponse(BaseModel):
    correct: bool
    score: int
    correct_answer: str
