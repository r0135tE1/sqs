# Fun with Flags — Backend

Python/FastAPI backend for the "Fun with Flags" flag-guessing game.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | FastAPI |
| Auth | JWT via `python-jose` + `passlib[bcrypt]` |
| Database | PostgreSQL (via SQLAlchemy async + asyncpg) |
| Migrations | Alembic |
| External API | [restcountries.com](https://restcountries.com) |
| Config | Environment variables / `.env` file |

---

## Project Structure

```
src/backend/
├── main.py                      # FastAPI app entry point
├── requirements.in             # Top-level dependencies (source for pip-compile)
├── requirements.lock           # Hash-pinned, fully-resolved dependencies
├── alembic.ini                  # Alembic configuration
├── .env.example                 # Copy to .env and fill in values
├── alembic/
│   ├── env.py                   # Async-compatible migration runner
│   └── versions/                # Migration scripts
└── app/
    ├── config.py                # Settings loaded from environment variables
    ├── dependencies.py          # FastAPI dependency: JWT auth guard
    ├── database/
    │   ├── engine.py            # Async engine, session factory, get_db dependency
    │   └── models.py            # SQLAlchemy ORM models (User, Highscore)
    ├── models/
    │   ├── game.py              # Pydantic schemas for session, flag question, answer
    │   ├── user.py              # Pydantic schemas for auth (register/login)
    │   └── highscore.py         # Pydantic schemas for highscores
    ├── repositories/
    │   ├── user.py              # DB access for users
    │   └── highscore.py         # DB access for highscores
    ├── routers/
    │   ├── game.py              # POST /game/session, GET /game/flag, POST /game/answer
    │   ├── auth.py              # POST /auth/register, POST /auth/login
    │   └── highscores.py        # GET /highscores/, GET /highscores/me, POST /highscores/
    └── services/
        ├── flag_cache.py        # In-memory cache for restcountries.com data (persisted to DB as fallback)
        ├── game_session.py      # GameSessionStore: server-side session and score tracking
        ├── auth.py              # Password hashing + JWT create/decode
        ├── highscore.py         # Highscore business logic
        └── user.py              # User business logic
```

---

## Endpoints

### Public

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check. Reports how many flags are cached. |
| `POST` | `/game/session` | Start a new game session. Returns `{ session_id }`. |
| `GET` | `/game/flag` | Get the next flag for a session. Query param: `session_id`. Returns `{ question_id, flag_svg, options }`. |
| `POST` | `/game/answer` | Submit an answer. Body: `{ question_id, answer }`. Returns `{ correct, score, correct_answer }`. |
| `POST` | `/auth/register` | Register a new user account. Body: `{ username, password }` |
| `POST` | `/auth/login` | Login and receive a JWT. Body: `{ username, password }` |

### Protected (require `Authorization: Bearer <token>`)

| Method | Path | Description |
|---|---|---|
| `GET` | `/highscores/` | List top 10 highscores across all users. |
| `GET` | `/highscores/me` | Get the authenticated user's own highscore. |
| `POST` | `/highscores/` | Save the best score from a game session. Body: `{ session_id }` |

Interactive API docs (Swagger UI) are available at `http://localhost:8000/docs`.

---

## How the Game Works

On startup, the app fetches the full country dataset (metadata + SVG images) from `restcountries.com/v3.1/all` and stores everything in memory (`FlagCache`). The data is also persisted to the `flags` table in the database so that a subsequent restart can recover from it if the external API is unreachable at that point.

### 1. Start a session

```
POST /game/session
→ { "session_id": "uuid" }
```

### 2. Get the next flag

```
GET /game/flag?session_id=<uuid>
→ {
    "question_id": "uuid",
    "flag_svg": "<svg xmlns=...>...</svg>",
    "options": ["Germany", "France", "Brazil", "Japan"]
  }
```

- `flag_svg` contains the full SVG markup inline — no CDN URL is ever sent to the client.
- The correct answer is **never** included in the response. It is stored server-side and looked up via `question_id`.
- The server automatically tracks which flags have already been shown in the session.

### 3. Submit an answer

```
POST /game/answer
Body: { "question_id": "uuid", "answer": "Germany" }
→ { "correct": true, "score": 3, "correct_answer": "Germany" }
```

- The score is tracked server-side: incremented on a correct answer, reset to 0 on a wrong answer.
- Each `question_id` can only be answered once.

### 4. Save the highscore (optional, authenticated users only)

```
POST /highscores/
Authorization: Bearer <token>
Body: { "session_id": "uuid" }
→ { "highscore": 5, "is_new_best": true }
```

The score is read server-side from the session — the client cannot submit an arbitrary value.

### 5. End of game

When all countries in a session have been shown, `GET /game/flag` returns `410 Gone` (distinct from the `404` returned for an unknown/expired session). The frontend treats this as a successful end-of-game: it shows a congratulations toast and starts a fresh round.

---

## Authentication Flow

1. `POST /auth/register` — password is hashed with bcrypt and stored in the DB.
2. `POST /auth/login` — credentials verified → server returns a signed JWT.
3. Client includes the JWT in subsequent requests: `Authorization: Bearer <token>`.
4. Protected routes use the `get_current_user` dependency to validate the token.

Token lifetime is controlled by `JWT_EXPIRE_MINUTES` (default: 60 minutes).

---

## Highscore Logic

One highscore row per user is stored. A new score is only saved if it is greater than 0 and greater than the user's current best. The leaderboard returns the top scores across all users.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `JWT_SECRET` | yes | — | Secret key for signing JWTs |
| `DATABASE_URL` | no | `postgresql+asyncpg://postgres:postgres@localhost:5432/funwithflags` | PostgreSQL connection string |
| `JWT_ALGORITHM` | no | `HS256` | JWT signing algorithm |
| `JWT_EXPIRE_MINUTES` | no | `60` | Token lifetime in minutes |
| `RESTCOUNTRIES_URL` | no | `https://restcountries.com/v3.1` | Base URL of the external flags API |
| `CORS_ORIGINS` | no | `["http://localhost:5173"]` | Allowed CORS origins |
| `LOG_LEVEL` | no | `INFO` | Logging level |

---

## Local Setup

### 1. Install and start PostgreSQL

PostgreSQL must be running locally before you start the server.

**macOS (Homebrew):**
```bash
brew install postgresql@16
brew services start postgresql@16
createuser -s postgres
createdb funwithflags
```

**Linux (apt):**
```bash
sudo apt update && sudo apt install postgresql postgresql-contrib
sudo systemctl enable --now postgresql
sudo -u postgres createdb funwithflags
```

**Windows:**
Download the installer from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/), set the password to `postgres`, then run:
```sql
CREATE DATABASE funwithflags;
```

### 2. Set up the Python environment

```bash
cd src/backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.lock
cp .env.example .env
# Edit .env and set JWT_SECRET
```

### 3. Apply database migrations

```bash
alembic upgrade head
```

### 4. Start the server

```bash
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`.

---

## Database Schema

**`users`**

| Column | Type | Notes |
|---|---|---|
| id | integer | primary key |
| username | varchar(50) | unique, indexed |
| hashed_password | text | bcrypt hash |
| created_at | timestamptz | set on insert |

**`highscores`**

| Column | Type | Notes |
|---|---|---|
| id | integer | primary key |
| user_id | integer | FK → users.id, unique |
| score | integer | personal best streak |
| created_at | timestamptz | set on insert |

---


## Backend Testing

### Prerequisites

Install dev dependencies (requires an active Python virtualenv):

```bash
cd src/backend
pip install -r requirements.lock -r dev-requirements.txt
```

> Integration tests spin up a real PostgreSQL container automatically via **testcontainers** — Docker must be running.

### Running Tests

```bash
cd src/backend

# All tests (unit + integration) with coverage report
pytest --cov=app --cov-report=term-missing

# Unit tests only — no Docker required
pytest tests/unit/

# Integration tests only — Docker must be running
pytest tests/integration/

# Enforce 80% coverage threshold (same check as CI)
pytest --cov=app --cov-report=xml --cov-fail-under=80
```

### Test Structure

```
src/backend/tests/
├── conftest.py                      # Shared fixture: seeded_flag_cache
├── unit/
│   ├── test_auth_service.py         # hash_password, verify_password, create/decode token
│   ├── test_flag_cache.py           # FlagCache in-memory logic
│   ├── test_game_session.py         # GameSessionStore: session, score, cleanup
│   └── test_dependencies.py         # get_current_user FastAPI dependency
└── integration/
    ├── conftest.py                  # PostgreSQL container + async HTTP client fixtures
    ├── test_health.py
    ├── test_auth.py                 # register / login flows
    ├── test_game.py                 # POST /game/session, GET /game/flag, POST /game/answer
    ├── test_highscores.py           # protected highscore endpoints
    ├── test_flag_cache_load.py      # Resilience: HTTP errors from restcountries.com
    └── test_security.py            # Input validation, auth bypass, score manipulation
```

Coverage is collected over the `app/` package. The XML report (`coverage.xml`) is forwarded to SonarQube in CI.

---

## Migrations (Alembic)

```bash
# Apply all migrations
alembic upgrade head

# Roll back one step
alembic downgrade -1

# Auto-generate a new migration after changing models.py
alembic revision --autogenerate -m "describe your change"
```
