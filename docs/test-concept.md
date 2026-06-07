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

**End-to-end tests** sit at the top and are deliberately few. They drive a real browser (Playwright) against the complete Docker Compose stack and cover the most critical user flows (see 2.4).

**Architecture tests** run as a separate `pytestarch` suite and enforce the dependency direction between layers (see 2.3).

### 2.1 Unit Tests

**Scope:** Pure functions and classes with no real I/O. External dependencies are mocked or replaced.

**Location:** `tests/unit/` — see the individual files for the concrete cases.

- **`test_auth_service.py`** — Password hashing round-trips (correct password verifies, wrong one is rejected) and the full JWT lifecycle
- **`test_flag_cache.py`** — Random flag selection: the returned question has the correct shape, always contains the correct answer among exactly four options, respects the exclude set (already-seen flags), and degrades gracefully to `None` on an empty / fully-excluded cache.
- **`test_dependencies.py`** — The `get_current_user` FastAPI dependency returns the username for a valid token and raises `HTTP 401` for invalid or expired ones.
- **`test_game_session.py`** — Session lifecycle (unique IDs, initial state, lookup), scoring (increment on correct, reset on wrong, personal-best preserved), the "seen flags" deduplication, single-use questions, and cleanup of expired sessions.

> **Mock strategy:** `FlagCache` state is set directly on the instance.

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
- **`test_game.py`** — The guest game flow: create session, fetch flags (valid inline SVG, exactly four options), submit answers (correct/wrong scoring, single-use questions), score streak/reset behaviour, and that seen flags are not repeated until exhausted (`404`).
- **`test_highscores.py`** — Saving and reading scores on the JWT-protected endpoints: personal-best logic, ordering, per-user isolation, and that every endpoint rejects missing/invalid tokens.
- **`test_flag_cache_load.py`** *(Resilience)* — `FlagCache.load()` against mocked HTTP responses: a 200 populates the cache, while HTTP errors, non-200 status, and malformed JSON leave it empty without crashing. Directly exercises the **Resilience** goal.
- **`test_security.py`** *(Security)* — Input validation (SQL injection, XSS, oversized username, weak/blank password → `422`), auth bypass (missing, forged, expired, wrong-secret, garbage tokens → `401`), and score manipulation (an arbitrary `score` in the body is ignored/rejected; the score is always read server-side).

### 2.3 Architecture Tests

**Scope:** Structural rules rather than behaviour. Using `pytestarch`, these tests assert the allowed dependency direction between layers so the architecture cannot silently erode.

**Location:** `app/tests/test_architecture.py`.

The rules enforce, among others: services must not import routers, the database, or dependencies; models must not import services, routers, or the database; the database layer must not import routers; routers must not import the database directly; and `config` must not import other app modules. This keeps the dependency flow pointing inward (routers → services → database) and supports the **Maintainability** goal.

### 2.4 End-to-End Tests

**Scope:** Full user flows exercised through a real browser (Playwright/Chromium) against the running Docker Compose stack — frontend served at `http://localhost`, talking to the live backend and PostgreSQL. These run as a dedicated CI job rather than as part of the `pytest` suite.

**Location:** `src/frontend/tests/e2e/` (config in `src/frontend/playwright.config.ts`, run via `npm run test:e2e`). Each test resets `localStorage`/`sessionStorage` before running, and registers users with unique names so runs are repeatable without DB cleanup.

Coverage by file:

- **`smoke.spec.ts`** — The single most important E2E test: load the app → a flag image renders → exactly four answer buttons with non-empty labels appear → clicking an answer shows a correct/wrong result strip and a Next/Try Again button. Proves the whole stack (frontend bundle, `/game/flag`, `/game/answer`, DB) is wired up end-to-end.
- **`game.spec.ts`** — Guest game flow (flag + four options, correct/wrong feedback), the "log in to track your high score" invite for anonymous users, signup (auto-login), login with a wrong password surfacing an error, the "Save your high score!" prompt shown to an anonymous user who loses with a score, and the highscores leaderboard modal for a logged-in user.
- **`auth.spec.ts`** — The auth round-trip that is genuinely irreplaceable by integration tests: register → auto-login → a JWT is persisted in `localStorage` → the session survives a page reload → the backend still accepts the token on a fresh protected request (Highscores) → logout clears the persisted state. Mocks would give false confidence here, so this exercises the real token lifecycle across the browser/backend boundary.

### 2.5 Security / Penetration Testing

Security tests are implemented as automated pytest integration tests (`tests/integration/test_security.py`, see 2.2) covering input validation, auth bypass, and score manipulation.

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
| `@playwright/test` | Browser-driven end-to-end tests against the Docker Compose stack |

All dependencies are pinned (with hashes) in `src/backend/requirements.lock`. CI installs them via `pip install --require-hashes -r requirements.lock`, so the test environment is fully reproducible.

### 3.2 Static Analysis & Coverage — SonarQube

SonarQube is the single static-analysis tool for this project. It runs as a service in CI and consumes the coverage report produced by `pytest-cov`. It covers:

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

The GitHub Actions pipeline (`.github/workflows/ci.yml`) runs separate jobs for **unit**, **integration**, and **architecture** tests, a **frontend type-check** (`npm run type-check`), and a **frontend E2E** job that builds and starts the full Docker Compose stack, waits for the backend (`/health`) and frontend to become healthy, then runs the Playwright suite (the report is uploaded as an artifact). The unit and integration jobs each upload their `coverage.xml` as an artifact; the **SonarQube** job downloads both, merges them, and runs the scan. SonarQube configuration lives in `sonar-project.properties`.

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

src/frontend/
├── tests/
│   └── e2e/                     # Playwright end-to-end tests (full stack)
│       ├── smoke.spec.ts
│       ├── game.spec.ts
│       └── auth.spec.ts
└── playwright.config.ts         # baseURL http://localhost; starts docker compose
```
