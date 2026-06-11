# Fun With Flags

A flag-guessing game where players are shown a country flag and must pick the correct country from four options. Correct answers extend your streak; a wrong answer resets it. Logged-in players can save their highscore and view the global leaderboard.

## Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3 + TypeScript, served by nginx |
| Backend | Python 3.12 + FastAPI |
| Database | PostgreSQL 16 |
| External API | [restcountries.com](https://restcountries.com) (v5, API key required) |

## Running with Docker

> **Requirements:** Docker Desktop, a free [restcountries.com](https://restcountries.com) API key

```bash
# 1. Generate the .env file with a random JWT secret and your API key
./setup.sh --key=<your-restcountries-api-key>

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

## Architecture Tests

The architecture tests verify that the layer separation of the backend is maintained (e.g. services do not import routers, models do not import the database).

### Setup

**1. Install pyenv** *(macOS)*
```bash
brew install pyenv
```

**2. Add pyenv to your shell** *(macOS — zsh)*
```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
```

**3. Install Python** *(macOS)*
```bash
# --enable-framework is required on macOS to avoid segfaults in venv
PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.12.0
pyenv global 3.12.0
```

**4. Create and activate a virtual environment**
```bash
cd src/backend
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**5. Install dependencies**
```bash
pip install --only-binary :all: --require-hashes -r requirements.lock
```

### Running the tests

> Make sure the virtual environment is active (`(venv)` visible in your prompt) before running the tests.

```bash
cd src
python -m pytest backend/app/tests/test_architecture.py -v
```


