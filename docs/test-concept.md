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

```
         /\
        /  \   E2E (Docker Compose)
       /----\
      /      \  Integration (routers + real DB)
     /--------\
    /          \  Unit (services, pure logic)
   /____________\
```

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

#### `tests/integration/test_flags.py`

| Test case | HTTP | Expected |
|---|---|---|
| `test_random_flag_ok` | `GET /flags/random` | `200`, valid `FlagResponse` shape |
| `test_random_flag_exclude_all` | `GET /flags/random?exclude=...` (all codes) | `404` |
| `test_random_flag_empty_cache` | `GET /flags/random` with empty cache | `404` |
| `test_random_flag_options_count` | Response `options` has 4 entries | shape check |

#### `tests/integration/test_highscores.py`

| Test case | HTTP | Expected |
|---|---|---|
| `test_get_highscores_authenticated` | `GET /highscores/` (valid JWT) | `200`, list |
| `test_get_highscores_no_token` | `GET /highscores/` (no header) | `403` |
| `test_get_highscores_invalid_token` | `GET /highscores/` (bad token) | `401` |
| `test_save_score_authenticated` | `POST /highscores/` (valid JWT) | `201` |
| `test_save_score_no_token` | `POST /highscores/` (no header) | `403` |
| `test_highscores_ordered_by_score_desc` | Save two scores, check order | order check |

#### `tests/integration/test_flag_cache_load.py` (Resilience)

| Test case | What is verified |
|---|---|
| `test_load_success` | `FlagCache.load()` with mocked HTTP 200 populates `_countries` |
| `test_load_http_error` | `FlagCache.load()` with mocked `httpx.HTTPError` leaves cache empty (no crash) |
| `test_load_bad_json` | `FlagCache.load()` with malformed response leaves cache empty (no crash) |
| `test_load_non_200_status` | `FlagCache.load()` with HTTP 500 response leaves cache empty |

> These directly test the **Resilience** quality goal: the service must not crash even when `restcountries.com` is down.

---

### 3.3 End-to-End Tests

**Scope:** Full happy-path flows against the running Docker Compose stack. Run separately (not in the standard `pytest` suite), triggered manually or in a dedicated CI job.

**Location:** `tests/e2e/`

**Tooling:** `httpx` calling `http://localhost:8000` (the running container).

#### Covered flows

1. **Guest game flow:** `GET /flags/random` 5× with growing `exclude` list → verify no repeat → final call with all excluded returns `404`.
2. **Registered user flow:** `POST /auth/register` → `POST /auth/login` → `POST /highscores/` → `GET /highscores/` → score appears in top 10.
3. **Token expiry flow:** Login → force-create an expired token → `GET /highscores/` returns `401`.

---

### 3.4 Security / Penetration Tests

#### Dynamic (DAST) — manual or scheduled CI job

Use **OWASP ZAP** in headless mode (`zap-baseline.py`) against the running Docker Compose stack.

Key scenarios to probe manually or via ZAP:
- Send forged / expired / missing JWT to every protected endpoint → expect `401`/`403`, not `500`.
- Send oversized payloads (`score: 99999999`) to `POST /highscores/` → verify no crash.
- Attempt SQL injection strings in `username` field of registration → DB constraint or validation must reject, not crash.

---

## 4. Coverage Requirement

The quality goal demands **≥80% code coverage**.

```bash
pytest --cov=app --cov-report=xml --cov-fail-under=80
```

The XML report (`coverage.xml`) is forwarded to SonarQube via `sonar-scanner` so that coverage is tracked and visualised there centrally.

Coverage is measured over the `app/` package (all routers, services, models, dependencies). `alembic/` and `main.py` bootstrap code are excluded from the measurement.

Expected coverage breakdown per module:

| Module | Expected coverage |
|---|---|
| `services/auth.py` | ~100% |
| `services/flag_cache.py` | ~95% |
| `dependencies.py` | ~100% |
| `routers/flags.py` | ~100% |
| `routers/auth.py` | ~95% |
| `routers/highscores.py` | ~95% |
| `config.py` / `database/` | ~70% (mostly config, hard to test exhaustively) |

---

## 5. Static Code Analysis — SonarQube

SonarQube is the single static analysis tool for this project. It covers:

- **Code smells** — maintainability issues, duplicated blocks, overly complex functions
- **Bugs** — likely runtime errors detected statically
- **Security hotspots** — e.g. hardcoded credentials, weak crypto usage
- **Coverage gate** — enforces ≥80% coverage based on the `coverage.xml` report

### CI integration

```yaml
# excerpt from .github/workflows/backend.yml
- name: Run tests and collect coverage
  run: pytest --cov=app --cov-report=xml --cov-fail-under=80

- name: SonarQube Scan
  uses: SonarSource/sonarqube-scan-action@v3
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
```

### `sonar-project.properties`

```properties
sonar.projectKey=fun-with-flags-backend
sonar.sources=app
sonar.tests=tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.qualitygate.wait=true
```

`sonar.qualitygate.wait=true` causes the CI step to fail if the SonarQube Quality Gate is not passed, which enforces the *"no open issues"* requirement.

---

## 6. Test Directory Layout

```
src/backend/
├── tests/
│   ├── conftest.py              # shared fixtures (async_client, test_db, seeded_flag_cache)
│   ├── unit/
│   │   ├── test_auth_service.py
│   │   ├── test_flag_cache.py
│   │   └── test_dependencies.py
│   ├── integration/
│   │   ├── test_health.py
│   │   ├── test_auth.py
│   │   ├── test_flags.py
│   │   ├── test_highscores.py
│   │   └── test_flag_cache_load.py
│   └── e2e/
│       └── test_full_flows.py
├── sonar-project.properties
├── pytest.ini                   # asyncio_mode = auto, testpaths = tests
└── dev-requirements.txt
```

---

## 7. CI Pipeline (GitHub Actions)

```yaml
# .github/workflows/backend.yml (sketch)
jobs:
  quality:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: test }
        ports: ["5432:5432"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r src/backend/dev-requirements.txt
      - run: pytest --cov=app --cov-report=xml --cov-fail-under=80   # unit + integration + coverage
      - uses: SonarSource/sonarqube-scan-action@v3                    # static analysis + quality gate
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
```

E2E tests run in a separate job that first does `docker compose up -d` and waits for the healthcheck.

---

## 8. Summary: Requirement Traceability

| Quality requirement | Addressed by |
|---|---|
| ≥80% test coverage | `pytest-cov --cov-fail-under=80` + SonarQube Quality Gate |
| Complete test pyramid | Unit → Integration → E2E → Pentest all documented and planned |
| No open static analysis issues | SonarQube Quality Gate blocks CI on any bug/hotspot finding |
| Resilience (restcountries.com down) | `test_flag_cache_load.py` — mocked HTTP errors leave cache empty without crash |
| Security — JWT on protected endpoints | `test_highscores.py` — no token / bad token / expired token all return 4xx |
