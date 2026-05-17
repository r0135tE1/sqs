import uuid


class _Question:
    def __init__(self, question_id: str, correct_answer: str, session_id: str) -> None:
        self.question_id = question_id
        self.correct_answer = correct_answer
        self.session_id = session_id


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

    def create_session(self) -> GameSession:
        session_id = str(uuid.uuid4())
        session = GameSession(session_id=session_id)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> GameSession | None:
        return self._sessions.get(session_id)

    def store_question(self, session_id: str, country_code: str, correct_answer: str) -> str:
        session = self._sessions.get(session_id)
        question_id = str(uuid.uuid4())
        self._questions[question_id] = _Question(
            question_id=question_id,
            correct_answer=correct_answer,
            session_id=session_id,
        )
        if session:
            session.seen.add(country_code)
            session.current_question_id = question_id
        return question_id

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
            session.current_question_id = None

        del self._questions[question_id]

        return correct, correct_answer, session.score if session else 0

    def get_best_score(self, session_id: str) -> int | None:
        """Return the highest streak achieved in this session, or None if session unknown."""
        session = self._sessions.get(session_id)
        if session is None:
            return None
        return max(session.score, session.best)

    def get_correct_answer(self, question_id: str) -> str | None:
        question = self._questions.get(question_id)
        return question.correct_answer if question else None

    # delete session and also orphaned questions (questions that never got answered)
    def delete_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
        orphaned = [qid for qid, q in self._questions.items() if q.session_id == session_id]
        for qid in orphaned:
            del self._questions[qid]


game_session_store = GameSessionStore()
