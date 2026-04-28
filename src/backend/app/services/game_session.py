import uuid


class _Question:
    def __init__(self, question_id: str, correct_answer: str, session_id: str, flag_url: str) -> None:
        self.question_id = question_id
        self.correct_answer = correct_answer
        self.session_id = session_id
        self.flag_url = flag_url


class GameSession:
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.score = 0
        self.best = 0
        self.seen: set[str] = set()
        self.current_question_id: str | None = None


class GameSessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, GameSession] = {}
        self._questions: dict[str, _Question] = {}
        # Keeps flag_url accessible for the image proxy even after the question is
        # answered (i.e., removed from _questions). Cleaned up lazily when the next
        # question for the same session is stored.
        self._images: dict[str, str] = {}

    def create_session(self) -> GameSession:
        session_id = str(uuid.uuid4())
        session = GameSession(session_id=session_id)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> GameSession | None:
        return self._sessions.get(session_id)

    def store_question(
        self, session_id: str, country_code: str, correct_answer: str, flag_url: str
    ) -> str:
        session = self._sessions.get(session_id)

        # Lazy cleanup: discard the previous question's image entry for this session.
        if session and session.current_question_id:
            self._images.pop(session.current_question_id, None)

        question_id = str(uuid.uuid4())
        self._questions[question_id] = _Question(
            question_id=question_id,
            correct_answer=correct_answer,
            session_id=session_id,
            flag_url=flag_url,
        )
        self._images[question_id] = flag_url

        if session:
            session.seen.add(country_code)
            session.current_question_id = question_id

        return question_id

    def get_image_url(self, question_id: str) -> str | None:
        """Return the real CDN URL for an image proxy request, or None if unknown."""
        return self._images.get(question_id)

    def validate_answer(self, question_id: str, answer: str) -> tuple[bool, str, int]:
        """Validate an answer; returns (correct, correct_answer, current_score).

        Raises ValueError when question_id is unknown.
        """
        question = self._questions.get(question_id)
        if question is None:
            raise ValueError("Unknown question_id")

        correct_answer = question.correct_answer
        correct = answer.strip() == correct_answer

        session = self._sessions.get(question.session_id)
        if session:
            if correct:
                session.score += 1
                session.best = max(session.best, session.score)
            else:
                session.score = 0
            # current_question_id is intentionally kept so store_question can
            # lazily clean up the _images entry when the next question arrives.

        del self._questions[question_id]

        return correct, correct_answer, session.score if session else 0

    def get_best_score(self, session_id: str) -> int | None:
        """Return the highest streak achieved in this session, or None if session unknown."""
        session = self._sessions.get(session_id)
        if session is None:
            return None
        return max(session.score, session.best)


game_session_store = GameSessionStore()
