import pytest

from app.services.game_session import GameSessionStore


def _store_with_session():
    store = GameSessionStore()
    session = store.create_session()
    return store, session.session_id


def _q(store, sid, code, name):
    return store.store_question(sid, code, name)


def test_create_session_returns_unique_ids():
    store = GameSessionStore()
    s1 = store.create_session()
    s2 = store.create_session()
    assert s1.session_id != s2.session_id


def test_create_session_initial_state():
    store = GameSessionStore()
    session = store.create_session()
    assert session.score == 0
    assert session.best == 0
    assert len(session.seen) == 0
    assert session.current_question_id is None


def test_get_session_returns_same_object():
    store = GameSessionStore()
    session = store.create_session()
    assert store.get_session(session.session_id) is session


def test_get_session_unknown_returns_none():
    store = GameSessionStore()
    assert store.get_session("nonexistent") is None


def test_store_question_adds_country_to_seen():
    store, sid = _store_with_session()
    _q(store, sid, "DE", "Germany")
    assert "DE" in store.get_session(sid).seen


def test_store_question_returns_unique_ids():
    store, sid = _store_with_session()
    qid1 = _q(store, sid, "DE", "Germany")
    qid2 = _q(store, sid, "FR", "France")
    assert qid1 != qid2


def test_validate_correct_answer_increments_score():
    store, sid = _store_with_session()
    qid = _q(store, sid, "DE", "Germany")
    correct, answer, score = store.validate_answer(qid, "Germany")
    assert correct is True
    assert answer == "Germany"
    assert score == 1


def test_validate_wrong_answer_resets_score():
    store, sid = _store_with_session()
    qid1 = _q(store, sid, "DE", "Germany")
    store.validate_answer(qid1, "Germany")
    qid2 = _q(store, sid, "FR", "France")
    store.validate_answer(qid2, "France")
    assert store.get_session(sid).score == 2

    qid3 = _q(store, sid, "IT", "Italy")
    correct, _, score = store.validate_answer(qid3, "WRONG")
    assert correct is False
    assert score == 0


def test_best_score_preserved_after_wrong_answer():
    store, sid = _store_with_session()
    for code, name in [("DE", "Germany"), ("FR", "France"), ("IT", "Italy")]:
        qid = _q(store, sid, code, name)
        store.validate_answer(qid, name)

    qid = _q(store, sid, "ES", "Spain")
    store.validate_answer(qid, "WRONG")

    assert store.get_best_score(sid) == 3


def test_best_score_updates_on_new_record():
    store, sid = _store_with_session()
    for code, name in [("DE", "Germany"), ("FR", "France"), ("IT", "Italy")]:
        qid = _q(store, sid, code, name)
        store.validate_answer(qid, name)
    assert store.get_best_score(sid) == 3

    qid = _q(store, sid, "ES", "Spain")
    store.validate_answer(qid, "Spain")
    assert store.get_best_score(sid) == 4


def test_validate_answer_removes_question():
    store, sid = _store_with_session()
    qid = _q(store, sid, "DE", "Germany")
    store.validate_answer(qid, "Germany")
    assert qid not in store._questions


def test_validate_answer_invalid_question_id_raises():
    store, _ = _store_with_session()
    with pytest.raises(ValueError):
        store.validate_answer("nonexistent-question", "Germany")


def test_get_best_score_unknown_session_returns_none():
    store = GameSessionStore()
    assert store.get_best_score("nonexistent") is None


def test_get_best_score_reflects_current_score_when_no_reset():
    store, sid = _store_with_session()
    for code, name in [("DE", "Germany"), ("FR", "France")]:
        qid = _q(store, sid, code, name)
        store.validate_answer(qid, name)
    assert store.get_best_score(sid) == 2


def test_delete_session_removes_session():
    store, sid = _store_with_session()
    store.delete_session(sid)
    assert store.get_session(sid) is None
    assert store.get_best_score(sid) is None


def test_delete_session_removes_orphaned_questions():
    store, sid = _store_with_session()
    qid = _q(store, sid, "DE", "Germany")
    store.delete_session(sid)
    assert qid not in store._questions


def test_delete_session_unknown_id_does_not_raise():
    store = GameSessionStore()
    store.delete_session("nonexistent")
