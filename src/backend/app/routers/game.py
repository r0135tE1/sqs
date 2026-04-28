import base64

from fastapi import APIRouter, HTTPException, status

from app.models.game import AnswerRequest, AnswerResponse, FlagQuestion, SessionResponse
from app.services.flag_cache import flag_cache
from app.services.game_session import game_session_store

router = APIRouter(prefix="/game", tags=["game"])


@router.post(
    "/session",
    status_code=status.HTTP_201_CREATED,
    summary="Start a new game session (public)",
    description="Creates a server-side game session that tracks seen flags and the current score.",
)
async def create_session() -> SessionResponse:
    session = game_session_store.create_session()
    return SessionResponse(session_id=session.session_id)


@router.get(
    "/flag",
    summary="Get the next flag for a session (public)",
    description=(
        "Returns a flag with four answer options and the flag image as a Base64 data URL. "
        "The correct answer is stored server-side and never sent to the client. "
        "Requires a valid session_id obtained from POST /game/session."
    ),
)
async def get_flag(session_id: str) -> FlagQuestion:
    session = game_session_store.get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )

    flag = flag_cache.random_flag(exclude=session.seen)
    if flag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No unseen flags left. All countries have been shown this session.",
        )

    svg = flag_cache.get_svg(flag["country_code"])
    if svg is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Flag image not available.",
        )

    question_id = game_session_store.store_question(
        session_id=session_id,
        country_code=flag["country_code"],
        correct_answer=flag["country_name"],
    )

    flag_data_url = f"data:image/svg+xml;base64,{base64.b64encode(svg).decode()}"

    return FlagQuestion(
        question_id=question_id,
        flag_url=flag_data_url,
        options=flag["options"],
    )


@router.post(
    "/answer",
    summary="Submit an answer (public)",
    description=(
        "Validates the player's answer against the server-stored correct answer. "
        "Returns whether the answer was correct and the updated streak score. "
        "Score is incremented server-side on correct answers and reset to 0 on wrong answers."
    ),
)
async def submit_answer(body: AnswerRequest) -> AnswerResponse:
    try:
        correct, correct_answer, score = game_session_store.validate_answer(
            question_id=body.question_id,
            answer=body.answer,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid question_id.",
        )

    return AnswerResponse(correct=correct, score=score, correct_answer=correct_answer)
