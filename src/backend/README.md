# Fun with Flags — Backend

Python/FastAPI backend for the "Fun with Flags" flag-guessing game.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI |
| Auth | JWT via `python-jose` + `passlib[bcrypt]` |
| Database | PostgreSQL (via SQLAlchemy async + asyncpg) |
| External API | [restcountries.com](https://restcountries.com) |
| Config | Environment variables / `.env` file |

---

## Project Structure

```
src/backend/
├── main.py                      # FastAPI app entry point
├── requirements.txt
├── alembic.ini                  # Alembic configuration
├── .env.example                 # Copy to .env and fill in values
├── alembic/
│   ├── env.py                   # Async-compatible migration runner
│   └── versions/
│       └── 001_initial.py       # Initial migration: users + highscores tables
└── app/
    ├── config.py                # Settings loaded from environment variables
    ├── dependencies.py          # FastAPI dependency: JWT auth guard
    ├── database/
    │   ├── engine.py            # Async engine, session factory, get_db dependency
    │   └── models.py            # SQLAlchemy ORM models (User, Highscore)
    ├── models/
    │   ├── flag.py              # Pydantic schemas for flag responses
    │   ├── user.py              # Pydantic schemas for auth (register/login)
    │   └── highscore.py         # Pydantic schemas for highscores
    ├── routers/
    │   ├── flags.py             # GET /flags/random
    │   ├── auth.py              # POST /auth/register, POST /auth/login
    │   └── highscores.py        # GET /highscores/, POST /highscores/
    └── services/
        ├── flag_cache.py        # In-memory cache for restcountries.com data
        └── auth.py              # Password hashing + JWT create/decode
```

---

## Endpoints

### Public

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check. Also reports how many flags are cached. |
| `GET` | `/flags/random` | Returns a random unseen flag for the current session. No auth required. |
| `POST` | `/auth/register` | Register a new user account. Body: `{ username, password }` |
| `POST` | `/auth/login` | Login and receive a JWT. Body: `{ username, password }` |

### Protected (require `Authorization: Bearer <token>`)

| Method | Path | Description |
|---|---|---|
| `GET` | `/highscores/` | List top highscores across all users. |
| `POST` | `/highscores/` | Save the current user's score. Body: `{ score }` |

The interactive API docs (Swagger UI) are available at `http://localhost:8000/docs` when the server is running.

---

## How Flags Work

On startup, the app fetches the full country dataset from `restcountries.com/v3.1/all` and stores it in memory (`FlagCache`).

`GET /flags/random` picks a random country from this cache and returns:

```json
{
  "country_code": "DE",
  "country_name": "Germany",
  "flag_url": "https://flagcdn.com/de.svg"
}
```

The frontend shows the flag, accepts a free-text guess, and validates it locally against `country_name`.
Comparison should be case-insensitive and trimmed:

```ts
guess.trim().toLowerCase() === country_name.toLowerCase()
```

### Session-based exclusion (no repeated flags)

To prevent the same flag from appearing twice in one game session, the frontend tracks all `country_code` values seen so far and passes them via the `exclude` query parameter:

```
GET /flags/random                               ← first flag
GET /flags/random?exclude=DE                    ← second flag
GET /flags/random?exclude=DE&exclude=FR         ← third flag
...
```

Example frontend logic:

```ts
const seen = new Set<string>()

async function nextFlag() {
  const params = [...seen].map(code => `exclude=${code}`).join("&")
  const res = await fetch(`/flags/random?${params}`)
  const flag = await res.json()
  seen.add(flag.country_code)
  return flag
}

function resetGame() {
  seen.clear()
}
```

When all 250 countries have been shown, the backend returns `404 Not Found`. The frontend should handle this as a "you've seen all flags" end-of-game condition.

**Resilience:** If `restcountries.com` is down at startup, the cache stays empty and `GET /flags/random` returns `502 Bad Gateway`. This matches the degradation strategy defined in ADR-006.

---

## Authentication Flow

1. User calls `POST /auth/register` → password is hashed with bcrypt and stored in the DB.
2. User calls `POST /auth/login` → credentials are verified → server returns a signed JWT.
3. Client includes the JWT in subsequent requests: `Authorization: Bearer <token>`.
4. Protected routes use the `get_current_user` dependency (`app/dependencies.py`) to validate the token and extract the username.

Token lifetime is controlled by `JWT_EXPIRE_MINUTES` (default: 60 minutes), per ADR-003.

---

## Local Setup

```bash
cd src/backend

# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env — at minimum set JWT_SECRET to a random string

# 4. Start the server
uvicorn main:app --reload
```

The server starts at `http://localhost:8000`.

> **Note:** The `GET /flags/random` endpoint works immediately (no database needed).
> Auth and highscore endpoints return `501 Not Implemented` until the database is connected.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/funwithflags` | PostgreSQL connection string |
| `JWT_SECRET` | `changeme-use-a-real-secret-in-production` | Secret key for signing JWTs — **change this!** |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `JWT_EXPIRE_MINUTES` | `60` | How long tokens are valid |
| `RESTCOUNTRIES_URL` | `https://restcountries.com/v3.1` | Base URL of the external flags API |

---

## Database Layer

### Schema

**`users`**

| Column | Type | Notes |
| --- | --- | --- |
| id | integer | primary key |
| username | varchar(50) | unique, indexed |
| hashed_password | text | bcrypt hash |
| created_at | timestamptz | set on insert |

**`highscores`**

| Column | Type | Notes |
| --- | --- | --- |
| id | integer | primary key |
| user_id | integer | FK → users.id |
| score | integer | streak length |
| created_at | timestamptz | set on insert |

Multiple highscore rows per user are allowed (one per finished game session). `GET /highscores/` returns the top 10 across all users.

### Migrations (Alembic)

```bash
# Apply all migrations (requires a running PostgreSQL)
alembic upgrade head

# Roll back one step
alembic downgrade -1

# Auto-generate a new migration after changing app/database/models.py
alembic revision --autogenerate -m "describe your change"
```

Migrations live in `alembic/versions/`. The connection URL is read from the `DATABASE_URL` environment variable — no need to edit `alembic.ini`.

---

## What's Not Implemented Yet

- **Tests** — unit and integration tests will be added separately.
- **Docker** — containerization and Docker Compose will be added separately.
