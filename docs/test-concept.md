# Backend Test Concept — Fun with Flags

## 1. Goals

This document describes the test strategy for the **Python/FastAPI backend** of "Fun with Flags". It maps each test level to the concrete quality goals from `docs/architecture/01_introduction_and_goals.md`:

| Quality Goal | How tests address it |
|---|---|
| **Testability & Verifiability** | Complete test pyramid, ≥80% line/branch coverage enforced in CI |
| **Resilience** | Unit tests for `FlagCache` failure paths; integration test with mocked HTTP error |
| **Security** | Dedicated auth tests for every JWT edge-case on protected endpoints |

---

## 2. Tools & Dependencies

| Tool | Purpose | added to `requirements.txt` section |
|---|---|---|
| `pytest` + `pytest-asyncio` | Async-capable test runner | `dev` |
| `httpx` | Async `TestClient` for FastAPI (already in prod deps) | — |
| `pytest-cov` | Coverage collection and enforcement | `dev` |
| `respx` | Mock `httpx` calls to `restcountries.com` | `dev` |
| `pytest-postgresql` / `testcontainers` | Real PostgreSQL in integration/e2e tests | `dev` |
| **SonarQube** | Static code analysis — coverage reporting, code smells, security hotspots | CI server |

```
# dev-requirements.txt (example)
pytest>=8.0
pytest-asyncio>=0.23
pytest-cov>=5.0
respx>=0.21
testcontainers[postgres]>=4.0
```

> SonarQube is not a pip package. It runs as a service in CI (e.g. via the `sonarqube` Docker image or SonarCloud). The CI step invokes `sonar-scanner` after `pytest-cov` generates an XML coverage report.

---

## 3. Test Pyramid

The test suite follows the classic test pyramid with three layers, each building on the one below.

**Unit tests** form the base and make up the majority of tests. They cover pure logic in isolation — no database, no HTTP, no external services. Dependencies are replaced with mocks or test doubles. Unit tests are fast, deterministic, and pinpoint exactly which function is broken.

**Integration tests** sit in the middle layer. They wire together the full HTTP stack (router → service → repository) against a real PostgreSQL instance spun up via `testcontainers`. This layer verifies that components interact correctly — that the right status codes are returned, database writes actually persist, and authentication is enforced end-to-end.

**End-to-end tests** sit at the top and are deliberately few. They run against the complete Docker Compose stack and cover the most critical user flows (guest game, registered user saving a highscore, token expiry). They are slower and more brittle by nature, so only the happy paths and a handful of failure scenarios are covered here.

### 3.1 Unit Tests

**Scope:** Pure functions and classes with no real I/O. External dependencies are mocked or replaced.

**Location:** `tests/unit/`

#### `tests/unit/test_auth_service.py`

| Test case | What is verified |
|---|---|
| `test_hash_and_verify_password` | `hash_password` + `verify_password` round-trip succeeds |
| `test_wrong_password_rejected` | `verify_password` returns `False` for wrong password |
| `test_create_token_contains_sub` | Decoded payload includes correct `sub` (username) |
| `test_create_token_expiry` | Decoded `exp` is approximately `now + jwt_expire_minutes` |
| `test_decode_valid_token` | `decode_token` returns correct username |
| `test_decode_expired_token` | `decode_token` returns `None` for an expired token |
| `test_decode_tampered_token` | `decode_token` returns `None` if signature is wrong |
| `test_decode_garbage_string` | `decode_token` returns `None` for arbitrary garbage |

#### `tests/unit/test_flag_cache.py`

| Test case | What is verified |
|---|---|
| `test_random_flag_empty_cache` | Returns `None` when `_countries` is empty |
| `test_random_flag_returns_correct_shape` | Returns dict with `country_code`, `country_name`, `flag_url`, `options` |
| `test_options_contain_correct_answer` | `country_name` is always in `options` |
| `test_options_length` | `options` has exactly 4 entries when ≥4 countries exist, fewer otherwise |
| `test_exclude_filters_correctly` | Excluded country codes never appear as the chosen flag |
| `test_all_excluded_returns_none` | Returns `None` when all country codes are in the exclude set |
| `test_count_reflects_loaded_data` | `count()` returns the number of loaded countries |

> **Mock strategy:** `_countries` is set directly on the `FlagCache` instance — no HTTP call needed.

#### `tests/unit/test_dependencies.py`

| Test case | What is verified |
|---|---|
| `test_get_current_user_valid_token` | Returns username for a valid token |
| `test_get_current_user_invalid_token` | Raises `HTTP 401` for an invalid token |
| `test_get_current_user_expired_token` | Raises `HTTP 401` for an expired token |

#### `tests/unit/test_game_session.py`

| Test case | What is verified |
|---|---|
| `test_create_session_returns_unique_ids` | Two sessions receive different UUIDs |
| `test_create_session_initial_state` | score, best, seen, current_question_id are initially empty/0 |
| `test_get_session_returns_same_object` | `get_session()` returns the same object |
| `test_get_session_unknown_returns_none` | Unknown session_id → `None` |
| `test_store_question_adds_country_to_seen` | Country code is added to `session.seen` |
| `test_store_question_returns_unique_ids` | Two questions receive different UUIDs |
| `test_validate_correct_answer_increments_score` | Correct answer → score +1, correct=True |
| `test_validate_wrong_answer_resets_score` | Wrong answer → score=0, correct=False |
| `test_best_score_preserved_after_wrong_answer` | `best` stays at 3 after score reset |
| `test_seen_flags_cleared_after_wrong_answer` | `seen` set is cleared on wrong answer |
| `test_cleanup_expired_removes_old_sessions` | Sessions inactive longer than TTL are removed |
| `test_cleanup_expired_keeps_active_sessions` | Active sessions are not removed |
| `test_validate_answer_removes_question` | Question is deleted from `_questions` after being answered |
| `test_validate_answer_invalid_question_id_raises` | Unknown question_id → `ValueError` |
| `test_get_best_score_unknown_session_returns_none` | Unknown session_id → `None` |
| `test_delete_session_removes_session` | Session and score are no longer retrievable |
| `test_delete_session_removes_orphaned_questions` | Open questions belonging to the session are also deleted |

---

### 3.2 Integration Tests

**Scope:** Full HTTP request → router → service → database round-trips. Uses a real PostgreSQL instance (via `testcontainers`) and a patched `flag_cache` where needed.

**Location:** `tests/integration/`

**Shared fixtures (`conftest.py`):**
- `async_client` — `httpx.AsyncClient` wrapping the FastAPI `app`, overrides `get_db` dependency with a test session connected to the container DB.
- `test_db` — creates / tears down the schema (runs Alembic migrations) before the test session.
- `seeded_flag_cache` — replaces the global `flag_cache._countries` with a fixed list of 10 fake countries so tests are deterministic.

#### `tests/integration/test_health.py`

| Test case | HTTP | Expected |
|---|---|---|
| `test_health_ok` | `GET /health` | `200`, body contains `flag_count` |

#### `tests/integration/test_auth.py`

| Test case | HTTP | Expected |
|---|---|---|
| `test_register_success` | `POST /auth/register` | `201`, `{"message": ...}` |
| `test_register_duplicate_username` | `POST /auth/register` (same name twice) | `409` |
| `test_login_success` | `POST /auth/login` | `200`, body contains `access_token` |
| `test_login_wrong_password` | `POST /auth/login` | `401` |
| `test_login_unknown_user` | `POST /auth/login` | `401` |

#### `tests/integration/test_game.py`

| Test case | HTTP | Expected |
|---|---|---|
| `test_create_session_returns_session_id` | `POST /game/session` | `201`, body contains `session_id` |
| `test_get_flag_returns_correct_fields` | `GET /game/flag?session_id=...` | `200`, keys: `question_id`, `flag_svg`, `options` |
| `test_get_flag_no_correct_answer_in_response` | `GET /game/flag?session_id=...` | `country_name` is never in the response |
| `test_get_flag_svg_is_valid` | `GET /game/flag?session_id=...` | `flag_svg` contains `<svg` markup, no CDN URL |
| `test_get_flag_has_four_options` | `GET /game/flag?session_id=...` | `options` has exactly 4 entries |
| `test_get_flag_unknown_session` | `GET /game/flag?session_id=invalid` | `404` |
| `test_answer_correct` | `POST /game/answer` | `200`, `correct=true`, `score=1` |
| `test_answer_wrong` | `POST /game/answer` | `200`, `correct=false`, `score=0` |
| `test_answer_invalid_question_id` | `POST /game/answer` with unknown question_id | `400` |
| `test_answer_question_can_only_be_used_once` | `POST /game/answer` submitted twice | `400` on second call |
| `test_score_increments_on_consecutive_correct_answers` | 3 correct answers in sequence | score reaches 3 |
| `test_score_resets_on_wrong_answer` | 3 correct, then 1 wrong | score=0 |
| `test_seen_flags_not_repeated` | 5× `GET /game/flag` | no SVG appears twice |
| `test_all_flags_shown_returns_404` | All flags in the session seen | `404` |

#### `tests/integration/test_highscores.py`

| Test case | HTTP | Expected |
|---|---|---|
| `test_get_highscores_authenticated` | `GET /highscores/` (valid JWT) | `200`, list |
| `test_get_highscores_no_token` | `GET /highscores/` (no header) | `401` |
| `test_get_highscores_invalid_token` | `GET /highscores/` (bad token) | `401` |
| `test_save_score_authenticated` | `POST /highscores/` (valid JWT), body: `{ "session_id": "..." }` | `201` |
| `test_save_score_no_token` | `POST /highscores/` (no header) | `401` |
| `test_save_score_unknown_session` | `POST /highscores/` with unknown `session_id` | `404` |
| `test_arbitrary_score_rejected` | Body `{ "score": 99999 }` instead of `session_id` | `422` |
| `test_save_score_updates_when_new_personal_best` | New record → `is_new_best=true`, `highscore=5` | `201` |
| `test_save_score_not_new_personal_best` | No new record → `is_new_best=false`, old record unchanged | `201` |
| `test_highscores_ordered_by_score_desc` | Save two scores, check order | order check |
| `test_get_my_highscore_authenticated` | `GET /highscores/me` (valid JWT) | `200`, `{ username, score }` |
| `test_get_my_highscore_no_token` | `GET /highscores/me` (no header) | `401` |
| `test_get_my_highscore_invalid_token` | `GET /highscores/me` (bad token) | `401` |
| `test_get_my_highscore_no_score_yet` | No highscore saved yet | `404` |
| `test_get_my_highscore_only_own` | User B sees only their own score, not user A's | isolation check |

#### `tests/integration/test_flag_cache_load.py` (Resilience)

| Test case | What is verified |
|---|---|
| `test_load_success` | `FlagCache.load()` with mocked HTTP 200 populates `_countries` |
| `test_load_http_error` | `FlagCache.load()` with mocked `httpx.HTTPError` leaves cache empty (no crash) |
| `test_load_bad_json` | `FlagCache.load()` with malformed response leaves cache empty (no crash) |
| `test_load_non_200_status` | `FlagCache.load()` with HTTP 500 response leaves cache empty |

> These directly test the **Resilience** quality goal: the service must not crash even when `restcountries.com` is down.

#### `tests/integration/test_security.py` (Penetration / Auth-Bypass)

| Test case | What is verified |
|---|---|
| `test_sql_injection_in_username_rejected` | SQL injection in username → `422` |
| `test_xss_payload_in_username_rejected` | XSS payload in username → `422` |
| `test_oversized_username_rejected` | Username > 50 characters → `422` |
| `test_blank_password_rejected` | Whitespace-only password → `422` |
| `test_too_short_password_rejected` | Password below minimum length → `422` |
| `test_no_token_get_highscores_rejected` | No Bearer token on `GET /highscores/` → `401` |
| `test_no_token_post_highscores_rejected` | No Bearer token on `POST /highscores/` → `401` |
| `test_forged_jwt_rejected` | Tampered JWT → `401` |
| `test_expired_jwt_rejected` | Expired JWT → `401` |
| `test_jwt_wrong_secret_rejected` | JWT signed with wrong secret → `401` |
| `test_garbage_token_rejected` | Non-JWT string as Bearer token → `401` |
| `test_arbitrary_score_in_body_rejected` | Body `{ "score": 99999999 }` instead of `session_id` → `422` |
| `test_nonexistent_session_rejected` | Unknown `session_id` in body → `404` |

---

### 3.3 End-to-End Tests

**Scope:** Full happy-path flows against the running Docker Compose stack. Run separately (not in the standard `pytest` suite), triggered manually or in a dedicated CI job.

**Location:** `tests/e2e/`

**Tooling:** `httpx` calling `http://localhost:8000` (the running container).

#### Covered flows

1. **Guest game flow:** `POST /game/session` → `GET /game/flag` (with `session_id`) 5× → `POST /game/answer` after each flag → after all flags shown: `GET /game/flag` returns `404`.
2. **Registered user flow:** `POST /auth/register` → `POST /auth/login` → `POST /game/session` → N× (`GET /game/flag` + `POST /game/answer`) → `POST /highscores/` with `{ session_id }` → `GET /highscores/` → score appears in top 10.
3. **Token expiry flow:** Login → force-create an expired token → `GET /highscores/` returns `401`.

---

### 3.4 Security / Penetration Tests

#### Automated — `tests/integration/test_security.py`

Security tests are implemented as automated pytest integration tests and run in the CI pipeline.
They cover three categories:

1. **Input Validation** — SQL injection, XSS, oversized username, blank/short password → all rejected with `422`
2. **Auth Bypass** — no token, forged JWT, expired JWT, wrong secret, garbage token → all rejected with `401`
3. **Score Manipulation** — submitting an arbitrary `score` value directly in the body is rejected with `422`; the score is always read server-side from the game session

#### Dynamic (DAST) — optional manual testing

**OWASP ZAP** can additionally be used in headless mode (`zap-baseline.py`) against the running
Docker Compose stack for dynamic analysis. This is not part of the automated CI pipeline.

---

## 4. Coverage Requirement

The quality goal demands **≥80% code coverage**.

```bash
pytest --cov=app --cov-report=xml --cov-fail-under=80
```

The XML report (`coverage.xml`) is forwarded to SonarQube via `sonar-scanner` so that coverage is tracked and visualised there centrally.

Coverage is measured over the `app/` package (all routers, services, models, dependencies). `alembic/` and `main.py` bootstrap code are excluded from the measurement.

---

## 5. Static Code Analysis — SonarQube

SonarQube is the single static analysis tool for this project. It covers:

- **Code smells** — maintainability issues, duplicated blocks, overly complex functions
- **Bugs** — likely runtime errors detected statically
- **Security hotspots** — e.g. hardcoded credentials, weak crypto usage
- **Coverage gate** — enforces ≥80% coverage based on the `coverage.xml` report

### CI integration

SonarQube runs as a dedicated job in the GitHub Actions pipeline after the unit and integration test jobs have completed. Both jobs upload their `coverage.xml` artifacts, which SonarQube then merges into a single coverage report. The Quality Gate is configured to block the pipeline if coverage drops below 80% or if any new bugs or security hotspots are introduced. Configuration is kept in `sonar-project.properties` at the backend root.

---

## 6. Test Directory Layout

```
src/backend/
├── tests/
│   ├── conftest.py              # shared fixture: seeded_flag_cache
│   ├── unit/
│   │   ├── test_auth_service.py
│   │   ├── test_flag_cache.py
│   │   ├── test_game_session.py
│   │   └── test_dependencies.py
│   └── integration/
│       ├── conftest.py          # PostgreSQL container + async_client fixture
│       ├── test_health.py
│       ├── test_auth.py
│       ├── test_game.py
│       ├── test_highscores.py
│       ├── test_flag_cache_load.py
│       └── test_security.py
├── app/
│   └── tests/
│       └── test_architecture.py # Architecture tests (pytestarch)
├── sonar-project.properties
├── pytest.ini                   # asyncio_mode = auto, testpaths = tests
└── requirements.lock
```

---

## 7. Summary: Requirement Traceability

| Quality requirement | Addressed by |
|---|---|
| ≥80% test coverage | `pytest-cov --cov-fail-under=80` + SonarQube Quality Gate |
| Complete test pyramid | Unit → Integration → E2E → Pentest all documented and planned |
| No open static analysis issues | SonarQube Quality Gate blocks CI on any bug/hotspot finding |
| Resilience (restcountries.com down) | `test_flag_cache_load.py` — mocked HTTP errors leave cache empty without crash |
| Security — JWT on protected endpoints | `test_highscores.py` — no token / bad token / expired token all return 4xx |
