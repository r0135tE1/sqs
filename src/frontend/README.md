# Fun with Flags — Frontend

Vue 3 + TypeScript frontend for the Fun with Flags country guessing game.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Vue 3 (`<script setup>`) | UI framework |
| TypeScript | Type safety |
| Scoped SFC styles (plain CSS) | Styling — each component ships its own `<style scoped>` block |
| Vite | Build tool and dev server |
| Vitest + `@vue/test-utils` + jsdom | Unit, component, and integration tests |
| Playwright | End-to-end tests |

---

## Project Structure

```
src/frontend/
├── index.html
├── vite.config.ts          # Vite + Vitest config (jsdom, v8 coverage)
├── playwright.config.ts    # E2E config (Chromium, Docker Compose stack)
├── tsconfig*.json
├── nginx.conf              # nginx config used in the Docker image
├── Dockerfile
├── app/
│   ├── main.ts
│   ├── config.ts           # API_URL constant (reads VITE_API_URL env var)
│   ├── App.vue             # Root: auth/session state, theme, navbar, error boundary
│   ├── api/
│   │   ├── client.ts       # apiFetch wrapper + ApiError / NetworkError types
│   │   └── errors.ts       # messageForError: maps errors to user-facing messages
│   ├── composables/
│   │   ├── useGame.ts          # game lifecycle: session, flags, scoring, save
│   │   └── useNotifications.ts # toast notification state (add/dismiss/dedupe)
│   └── components/
│       ├── GameBoard.vue        # Flag display, answer buttons, score tracking
│       ├── SaveScorePrompt.vue  # Prompt inviting anonymous players to sign up
│       ├── BaseModal.vue        # Reusable, accessible modal shell (dialog role, focus trap)
│       ├── AuthModal.vue        # Combined login / signup form
│       ├── HighscoresModal.vue  # Global leaderboard
│       ├── ErrorBoundary.vue    # Catches render errors, shows fallback UI
│       └── NotificationStack.vue # Renders the active toast notifications
└── tests/                  # Vitest (unit/component/integration) + Playwright e2e
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Backend API base URL |

Set in a `.env.local` file for local development, or passed as a build arg in Docker.

---

## Local Setup

```bash
cd src/frontend
npm install
```

Copy the backend URL if it differs from the default:
```bash
echo "VITE_API_URL=http://localhost:8000" > .env.local
```

Start the dev server:
```bash
npm run dev
```

Vite starts at `http://localhost:5173` with hot module replacement.

> The backend must be running at `VITE_API_URL` before the app is usable.

---

## Building for Production

```bash
npm run build
```

Runs a type check then compiles the app into `dist/`.

To preview the production build locally:
```bash
npm run preview
```

---

## Testing

Vitest covers unit, component, and integration tests (in `jsdom`, with all network calls mocked); Playwright drives end-to-end tests against the running Docker Compose stack. See [docs/test-concept.md](../../docs/test-concept.md) for the full strategy.

```bash
npm run test            # Vitest in watch mode
npm run test:run        # Vitest once (CI mode)
npm run test:coverage   # Vitest once with V8 coverage (lcov → SonarQube)
npm run test:ui         # Vitest interactive UI
npm run test:e2e        # Playwright e2e (requires the Docker Compose stack)
npm run type-check      # vue-tsc type check (no emit)
```

Tests live under `tests/` — `unit/`, `component/`, and `integration/` run in Vitest; `e2e/` runs in Playwright and is excluded from the Vitest run.

---

## Docker

The frontend is built and served via nginx in Docker. See the root [docker-compose.yml](../../docker-compose.yml) to run the full stack.

The `VITE_API_URL` build argument controls which backend the built app points to:
```yaml
build:
  context: ./src/frontend
  args:
    VITE_API_URL: http://localhost:8000
```
