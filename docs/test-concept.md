# Test Concept — Fun with Flags

## 1. Goals

This document describes the test strategy for the "Fun with Flags" application. It maps each test level to the concrete quality goals from `docs/architecture/01_introduction_and_goals.md`. The application has **two independently tested code bases** — the Python/FastAPI backend (section 2) and the Vue/TypeScript frontend (section 3) — each with its own test pyramid and coverage report, merged into a single SonarQube scan.

| Quality Goal | How tests address it |
| --- | --- |
| **Testability & Verifiability** | Complete test pyramid on both backend and frontend, ≥80% line/branch coverage enforced via the SonarQube quality gate in CI |
| **Resilience** | Backend unit tests for `FlagCache` failure paths and integration tests with mocked HTTP errors; frontend component/integration tests for offline endpoints, retry banners, and session-expiry handling |
| **Security** | Dedicated auth and input-validation tests for JWT and injection edge-cases on protected endpoints |
| **Maintainability** | Architecture tests (`pytestarch`) enforce the layering rules so the structure cannot erode |

---

## 2. Backend Tests

The backend suite follows the classic test pyramid, with an additional architecture layer that runs alongside it.

**Unit tests** form the base and make up the majority of tests. They cover pure logic with all external dependencies mocked or replaced.

**Integration tests** sit in the middle. They wire together the full HTTP stack (router → service → repository) against a real PostgreSQL instance spun up via `testcontainers`, verifying status codes, persistence, and end-to-end authentication.

**Architecture tests** run as a separate `pytestarch` suite and enforce the dependency direction between layers (see 2.3).

End-to-end coverage of the full stack lives in the frontend Playwright suite (see 3.4), which drives the complete Docker Compose deployment through the browser.

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

### 2.4 Security / Penetration Testing

Security tests are implemented as automated pytest integration tests (`tests/integration/test_security.py`, see 2.2) and run in CI, covering input validation, auth bypass, and score manipulation.

---

## 3. Frontend Tests

The frontend (`src/frontend`, Vue 3 + TypeScript) has its own test pyramid run with **Vitest** in a `jsdom` environment, plus a thin layer of **Playwright** end-to-end tests. In line with the *headless frontend* decision (see `docs/architecture/09_architecture_decisions.md`), the frontend holds no business logic — so the tests focus on rendering, user interaction, API wiring, and error/recovery handling rather than game rules.

All network access in the Vitest layers is mocked (`tests/helpers/fetchMock.ts`); no real backend is involved. Coverage is collected by the V8 provider over `app/**` (excluding `main.ts` and `env.d.ts`) and written as `lcov.info`.

### 3.1 Unit Tests

**Scope:** Pure TypeScript modules and composables with no component mounting.

**Location:** `tests/unit/`

- **`apiClient.test.ts`** — The `apiFetch` wrapper: parses JSON on success, handles `204 No Content`, attaches the `Authorization` header when a token is given, encodes JSON bodies with the correct `Content-Type`, and surfaces `NetworkError` / `ApiError` (with backend detail or a default) on failures.
- **`useNotifications.test.ts`** — The notification composable: adds notifications with the right type/message, auto-dismisses after the default or a custom duration, persists when duration is `0`, dismisses by id (no-op for unknown ids), and dedupes by `type+message` (resetting the timer) without deduping across different types.

### 3.2 Component Tests

**Scope:** Individual Vue components mounted in isolation with `@vue/test-utils`, asserting rendered output, emitted events, and interaction state.

**Location:** `tests/component/`

- **`BaseModal.test.ts`** — Open/closed rendering, optional title/header, slot content, and `close` emission on backdrop and close-button clicks; plus accessibility: dialog ARIA attributes (`role`, `aria-modal`, `aria-labelledby`), `Escape` to close, and Tab/Shift+Tab focus trapping.
- **`AuthModal.test.ts`** — Login vs. signup mode (titles, button labels), client-side validation in signup mode (short username, password without a digit) while login mode passes input through, `submit`/`switch` emissions, external error display, and form reset on close.
- **`HighscoresModal.test.ts`** — Loading spinner, error/empty/populated states, rank gold/silver/bronze styling for the top 3, refetch when reopened, and that the `Authorization` header is sent.
- **`SaveScorePrompt.test.ts`** — The anonymous save-score prompt: open/closed rendering, the call-to-action copy, and `signup` / `login` / `dismiss` emissions on the respective buttons and backdrop.
- **`ErrorBoundary.test.ts`** — Renders the default slot normally, shows the fallback UI when a child throws, and resets on "Try again".
- **`GameBoard.test.ts`** — Loading skeleton, flag + four answer buttons, anonymous vs. authenticated highscore label, `session-expired` emission on a `401` from `/highscores/me`, button disabling after submit, and correct/wrong result strips with answer highlighting.
- **`GameBoard.recovery.test.ts`** — Error/recovery paths: retry banner when `loadFlag` fails and recovery via Retry, discarding a stale session on a `404` from `/game/answer`, saving the score and emitting `new-highscore` on a new best, and relying on notification dedupe so offline answers don't stack toasts.

> The game logic these last two files exercise lives in the `useGame` composable; it is covered through the GameBoard component tests rather than a separate unit test. Likewise the `messageForError` helper (`app/api/errors.ts`) is covered via the App and HighscoresModal tests.

### 3.3 Integration Tests

**Scope:** The whole `App` mounted with a mocked `fetch`, exercising full user flows across components and the auth/session state.

**Location:** `tests/integration/`

- **`app-flows.test.ts`** — Sign-up → logged-in state, login failure messaging, the login prompt shown to an anonymous user after a wrong answer with a non-zero score, state/UI cleanup on logout, and the "new highscore" toast when the backend reports a new best.
- **`app-errors.test.ts`** — Username-taken conflict on signup, network errors in the signup form, generic login error on a non-`401` response, the session-expired warning toast when `GameBoard` emits `401`, and double-submit prevention on the login form.

### 3.4 End-to-End Tests

**Scope:** Critical user journeys driven by **Playwright** (Chromium) against the complete app served by the Docker Compose stack (`baseURL: http://localhost`).

**Location:** `tests/e2e/`

- **`smoke.spec.ts`** — The app loads, shows a flag, and accepts an answer.
- **`game.spec.ts`** — Flag with four options, the login invitation for anonymous users, correct/wrong feedback, signup→login, login with a wrong password, the signup prompt after a wrong answer with score, and opening the highscores leaderboard as a logged-in user.
- **`auth.spec.ts`** — Register → auto-login → session persists across a page reload (the JWT is stored in `localStorage`).

---

## 4. Test Environment & Tooling

### 4.1 Tools

**Backend:**

| Tool | Purpose |
| --- | --- |
| `pytest` + `pytest-asyncio` | Async-capable test runner |
| `httpx` | Async client for driving the FastAPI app in tests |
| `pytest-cov` | Coverage collection (XML report for SonarQube) |
| `respx` | Mock `httpx` calls to `restcountries.com` |
| `testcontainers[postgres]` | Real PostgreSQL instance for integration tests |
| `pytestarch` | Architecture / layering rules as tests |
| `@playwright/test` | Browser-driven end-to-end tests against the Docker Compose stack |

All backend dependencies are pinned (with hashes) in `src/backend/requirements.lock`. CI installs them via `pip install --require-hashes -r requirements.lock`, so the test environment is fully reproducible.

**Frontend:**

| Tool | Purpose |
| --- | --- |
| `vitest` | Test runner for unit, component, and integration tests |
| `jsdom` | Browser-like DOM environment for Vitest |
| `@vue/test-utils` | Mounting and interacting with Vue components |
| `@vitest/coverage-v8` | Coverage collection (V8 provider, `lcov` report for SonarQube) |
| `@playwright/test` | End-to-end tests against the Docker Compose stack (Chromium) |

Frontend dependencies are locked via `src/frontend/package-lock.json`; CI installs them with `npm ci --ignore-scripts`.

### 4.2 Static Analysis & Coverage — SonarQube

SonarQube is the single static-analysis tool for this project. It runs as a service in CI and consumes the coverage reports produced by `pytest-cov` (backend) and Vitest's V8 provider (frontend). It covers:

- **Code smells** — maintainability issues, duplication, overly complex functions
- **Bugs** — likely runtime errors detected statically
- **Security hotspots** — e.g. hardcoded credentials, weak crypto usage
- **Coverage gate** — enforces the ≥80% target based on the merged coverage report

SonarQube consumes coverage from **both** code bases: the backend Python reports (`sonar.python.coverage.reportPaths`) and the frontend `lcov.info` (`sonar.typescript.lcov.reportPaths` / `sonar.javascript.lcov.reportPaths`). Backend coverage is measured over the `app/` package (routers, services, models, dependencies); frontend coverage over `app/**`. Test files, `alembic/`, `src/backend/main.py`, and `src/frontend/app/main.ts` are excluded. Each test job produces a coverage report locally, e.g.:

```bash
pytest --cov=app --cov-report=xml      # backend
npm run test:coverage                  # frontend (lcov)
```

The 80% threshold is **not** enforced by the test runners themselves — it is the SonarQube quality gate that blocks the pipeline when coverage drops below target or when new bugs / security hotspots are introduced.

### 4.3 CI Integration

The GitHub Actions pipeline (`.github/workflows/ci.yml`) runs separate jobs for the backend **unit**, **integration**, and **architecture** tests, and for the frontend a **type-check** (`npm run type-check`), **unit & component tests** (`npm run test:coverage`, via Vitest), and **end-to-end tests** (Playwright/Chromium against the Docker Compose stack). The backend unit/integration jobs upload their `coverage.xml` and the frontend unit job uploads its `lcov.info` as artifacts; the **SonarQube** job downloads them, merges the reports, and runs a single scan. SonarQube configuration lives in `sonar-project.properties`.

---

## 5. Test Directory Layout

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
│   ├── helpers/
│   │   └── fetchMock.ts          # shared fetch mock for Vitest layers
│   ├── unit/
│   │   ├── apiClient.test.ts
│   │   └── useNotifications.test.ts
│   ├── component/
│   │   ├── BaseModal.test.ts
│   │   ├── AuthModal.test.ts
│   │   ├── HighscoresModal.test.ts
│   │   ├── SaveScorePrompt.test.ts
│   │   ├── ErrorBoundary.test.ts
│   │   ├── GameBoard.test.ts
│   │   └── GameBoard.recovery.test.ts
│   ├── integration/
│   │   ├── app-flows.test.ts
│   │   └── app-errors.test.ts
│   └── e2e/                      # Playwright (Chromium) — excluded from Vitest
│       ├── smoke.spec.ts
│       ├── game.spec.ts
│       └── auth.spec.ts
├── vite.config.ts                # Vitest config (jsdom, v8 coverage → lcov)
├── playwright.config.ts          # e2e config (testDir: tests/e2e, docker compose)
└── package-lock.json             # locked dependencies
```
