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
├── requirements.txt
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
| `GET` | `/flags/random` | Returns a random flag with 4 answer options. |
| `POST` | `/auth/register` | Register a new user account. Body: `{ username, password }` |
| `POST` | `/auth/login` | Login and receive a JWT. Body: `{ username, password }` |

### Protected (require `Authorization: Bearer <token>`)

| Method | Path | Description |
|---|---|---|
| `GET` | `/highscores/` | List top highscores across all users. |
| `POST` | `/highscores/` | Save the current user's score. Body: `{ score }` |

Interactive API docs (Swagger UI) are available at `http://localhost:8000/docs`.

---

## How Flags Work

On startup, the app fetches the full country dataset from `restcountries.com/v3.1/all` and stores it in memory (`FlagCache`).

`GET /flags/random` picks a random country and returns it with 3 random wrong options:

```json
{
  "country_code": "DE",
  "country_name": "Germany",
  "flag_url": "https://flagcdn.com/de.svg",
  "options": ["Germany", "France", "Brazil", "Japan"]
}
```

To prevent the same flag from appearing twice in one session, pass previously seen country codes via `exclude`:

```
GET /flags/random?exclude=DE&exclude=FR
```

When all countries have been shown, the endpoint returns `404`. The frontend treats this as end-of-game.

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
pip install -r requirements.txt
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

## Migrations (Alembic)

```bash
# Apply all migrations
alembic upgrade head

# Roll back one step
alembic downgrade -1

# Auto-generate a new migration after changing models.py
alembic revision --autogenerate -m "describe your change"
```
