# Fun With Flags

A flag-guessing game where players are shown a country flag and must pick the correct country from four options. Correct answers extend your streak; a wrong answer resets it. Logged-in players can save their highscore and view the global leaderboard.

## Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3 + TypeScript + Tailwind CSS, served by nginx |
| Backend | Python 3.12 + FastAPI |
| Database | PostgreSQL 16 |
| External API | [restcountries.com](https://restcountries.com) |

## Running with Docker

> **Requirements:** Docker Desktop

```bash
# 1. Copy the example env file and set a JWT secret
cp src/backend/.env.example src/backend/.env
# Edit src/backend/.env and set JWT_SECRET to a random string

# 2. Build and start all containers
docker compose up --build
```

Open **http://localhost** in your browser.

| Service | URL |
|---|---|
| Frontend | http://localhost |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

```bash
# Stop containers
docker compose down

# Stop and wipe the database
docker compose down -v
```

## Running Locally (without Docker)

See [src/backend/README.md](src/backend/README.md) and [src/frontend/README.md](src/frontend/README.md) for local setup instructions.

## Project Structure

```
.
├── docker-compose.yml
├── src/
│   ├── backend/        # FastAPI app
│   └── frontend/       # Vue 3 app
└── docs/               # Architecture documentation
```
