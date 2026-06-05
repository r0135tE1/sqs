# Backend Test Concept — Fun with Flags

## 1. Goals

This document describes the test strategy for the "Fun with Flags" application. It maps each test level to the concrete quality goals from `docs/architecture/01_introduction_and_goals.md`:

| Quality Goal | How tests address it |
| --- | --- |
| **Testability & Verifiability** | Complete test pyramid, ≥80% line/branch coverage enforced via the SonarQube quality gate in CI |
| **Resilience** | Unit tests for `FlagCache` failure paths; integration tests with mocked HTTP errors |
| **Security** | Dedicated auth and input-validation tests for JWT and injection edge-cases on protected endpoints |
| **Maintainability** | Architecture tests (`pytestarch`) enforce the layering rules so the structure cannot erode |

---

## 2. Test Pyramid

The suite follows the classic test pyramid, with an additional architecture layer that runs alongside it.

**Unit tests** form the base and make up the majority of tests. They cover pure logic with all external dependencies mocked or replaced.

**Integration tests** sit in the middle. They wire together the full HTTP stack (router → service → repository) against a real PostgreSQL instance spun up via `testcontainers`, verifying status codes, persistence, and end-to-end authentication.

**End-to-end tests** sit at the top and are deliberately few. They run against the complete Docker Compose stack and cover the most critical user flows. *(Planned — not yet implemented.)*

**Architecture tests** run as a separate `pytestarch` suite and enforce the dependency direction between layers (see 2.3).

### 2.1 Unit Tests

**Scope:** Pure functions and classes with no real I/O. External dependencies are mocked or replaced.

**Location:** `tests/unit/` — see the individual files for the concrete cases.

- **`test_auth_service.py`** — Password hashing round-trips (correct password verifies, wrong one is rejected) and the full JWT lifecycle
- **`test_flag_cache.py`** — Random flag selection: the returned question has the correct shape, always contains the correct answer among exactly four options, respects the exclude set (already-seen flags), and degrades gracefully to `None` on an empty / fully-excluded cache.
- **`test_dependencies.py`** — The `get_current_user` FastAPI dependency returns the username for a valid token and raises `HTTP 401` for invalid or expired ones.
- **`test_game_session.py`** — Session lifecycle (unique IDs, initial state, lookup), scoring (increment on correct, reset on wrong, personal-best preserved), the "seen flags" deduplication, single-use questions, and cleanup of expired sessions.

> **Mock strategy:** `FlagCache` state is set directly on the instance — no HTTP call needed.

### 2.2 Integration Tests

**Scope:** Full HTTP request → router → service → database round-trips against a real PostgreSQL instance (via `testcontainers`), with the flag cache seeded deterministically.

**Location:** `tests/integration/`

**Shared fixtures:**

- `pg_container` / `db_async_url` (`tests/integration/conftest.py`) — start a session-scoped PostgreSQL container and expose its async (`asyncpg`) URL.
- `async_client` — an `httpx.AsyncClient` wrapping the FastAPI `app` with the `get_db` dependency overridden to use the container database.
- `seeded_flag_cache` (root `tests/conftest.py`) — replaces the global flag cache with a fixed set of 10 fake countries (and SVGs) so tests are deterministic. The root conftest also sets a test `JWT_SECRET`.

Coverage by file:

- **`test_health.py`** — `GET /health` returns `200` and reports the loaded flag count.
- **`test_auth.py`** — Registration (success, duplicate username → `409`) and login (success, wrong password and unknown user → `401`).
- **`test_game.py`** — The guest game flow: create session, fetch flags (valid inline SVG, exactly four options, correct answer never leaked), submit answers (correct/wrong scoring, single-use questions), score streak/reset behaviour, and that seen flags are not repeated until exhausted (`404`).
- **`test_highscores.py`** — Saving and reading scores on the JWT-protected endpoints: personal-best logic, ordering, per-user isolation, and that every endpoint rejects missing/invalid tokens.
- **`test_flag_cache_load.py`** *(Resilience)* — `FlagCache.load()` against mocked HTTP responses: a 200 populates the cache, while HTTP errors, non-200 status, and malformed JSON leave it empty without crashing. Directly exercises the **Resilience** goal.
- **`test_security.py`** *(Security)* — Input validation (SQL injection, XSS, oversized username, weak/blank password → `422`), auth bypass (missing, forged, expired, wrong-secret, garbage tokens → `401`), and score manipulation (an arbitrary `score` in the body is ignored/rejected; the score is always read server-side).

### 2.3 Architecture Tests

**Scope:** Structural rules rather than behaviour. Using `pytestarch`, these tests assert the allowed dependency direction between layers so the architecture cannot silently erode.

**Location:** `app/tests/test_architecture.py` (run as a dedicated CI job: `pytest app/tests -v`).

The rules enforce, among others: services must not import routers, the database, or dependencies; models must not import services, routers, or the database; the database layer must not import routers; routers must not import the database directly; and `config` must not import other app modules. This keeps the dependency flow pointing inward (routers → services → database) and supports the **Maintainability** goal.

### 2.4 End-to-End Tests *(planned)*

**Scope:** Full happy-path flows against the running Docker Compose stack, driven by `httpx` against `http://localhost:8000`. These are not part of the standard `pytest` suite and are not implemented yet — the intended flows are:

1. **Guest game flow:** create session → fetch flag + answer repeatedly → `404` once all flags are seen.
2. **Registered user flow:** register → login → play → save highscore → score appears in the top 10.
3. **Token expiry flow:** login → use an expired token → protected endpoint returns `401`.

### 2.5 Security / Penetration Testing

Security tests are implemented as automated pytest integration tests (`tests/integration/test_security.py`, see 2.2) and run in CI, covering input validation, auth bypass, and score manipulation.

---

## 3. Test Environment & Tooling

### 3.1 Tools

| Tool | Purpose |
| --- | --- |
| `pytest` + `pytest-asyncio` | Async-capable test runner |
| `httpx` | Async client for driving the FastAPI app in tests |
| `pytest-cov` | Coverage collection (XML report for SonarQube) |
| `respx` | Mock `httpx` calls to `restcountries.com` |
| `testcontainers[postgres]` | Real PostgreSQL instance for integration tests |
| `pytestarch` | Architecture / layering rules as tests |

All dependencies are pinned (with hashes) in `src/backend/requirements.lock`. CI installs them via `pip install --require-hashes -r requirements.lock`, so the test environment is fully reproducible.

### 3.2 Static Analysis & Coverage — SonarQube

SonarQube is the single static-analysis tool for this project. It is not a pip package — it runs as a service in CI and consumes the coverage report produced by `pytest-cov`. It covers:

- **Code smells** — maintainability issues, duplication, overly complex functions
- **Bugs** — likely runtime errors detected statically
- **Security hotspots** — e.g. hardcoded credentials, weak crypto usage
- **Coverage gate** — enforces the ≥80% target based on the merged coverage report

Coverage is measured over the `app/` package (routers, services, models, dependencies); test files, `alembic/`, and `main.py` bootstrap code are excluded. Each test job produces a coverage report locally, e.g.:

```bash
pytest --cov=app --cov-report=xml
```

The 80% threshold is **not** enforced by `pytest` itself — it is the SonarQube quality gate that blocks the pipeline when coverage drops below target or when new bugs / security hotspots are introduced.

### 3.3 CI Integration

The GitHub Actions pipeline (`.github/workflows/ci.yml`) runs separate jobs for **unit**, **integration**, and **architecture** tests, plus a **frontend type-check** (`npm run type-check`; the frontend currently has no unit/integration tests). The unit and integration jobs each upload their `coverage.xml` as an artifact; the **SonarQube** job downloads both, merges them, and runs the scan. SonarQube configuration lives in `sonar-project.properties`.

---

## 4. Test Directory Layout

```text
src/backend/
├── tests/
│   ├── conftest.py              # sets test JWT_SECRET; seeded_flag_cache fixture
│   ├── unit/
│   │   ├── test_auth_service.py
│   │   ├── test_flag_cache.py
│   │   ├── test_game_session.py
│   │   └── test_dependencies.py
│   └── integration/
│       ├── conftest.py          # PostgreSQL container + async_client fixtures
│       ├── test_health.py
│       ├── test_auth.py
│       ├── test_game.py
│       ├── test_highscores.py
│       ├── test_flag_cache_load.py
│       └── test_security.py
├── app/
│   └── tests/
│       └── test_architecture.py # architecture / layering rules (pytestarch)
├── sonar-project.properties
├── pytest.ini                   # asyncio_mode = auto, testpaths = tests
└── requirements.lock            # pinned, hash-verified dependencies
```