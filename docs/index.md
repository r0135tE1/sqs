# Fun With Flags

Welcome to the documentation for **Fun With Flags** — a flag-guessing game.

## What is Fun With Flags?

Players are shown the flag of a country and have to pick the correct country from
four options. Every correct answer extends your streak, while a wrong answer
resets it back to zero. Logged-in players can save their highscore and compare
themselves against others on the global leaderboard.

## Tech stack

| Layer        | Technology                                              |
| ------------ | ------------------------------------------------------- |
| Frontend     | Vue 3 + TypeScript, served by nginx      |
| Backend      | Python 3.12 + FastAPI                                   |
| Database     | PostgreSQL 16                                           |
| External API | [restcountries.com](https://restcountries.com)          |

## Where to go next

- **[Usage](usage.md)** — run the application and start playing.
- **[Architecture](architecture/01_introduction_and_goals.md)** — how the system
  is built.

