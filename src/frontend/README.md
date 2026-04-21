# Fun with Flags — Frontend

Vue 3 + TypeScript frontend for the Fun with Flags country guessing game.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Vue 3 | UI framework |
| TypeScript | Type safety |
| Tailwind CSS v4 | Styling |
| Vite | Build tool and dev server |

---

## Project Structure

```
src/frontend/
├── index.html
├── vite.config.ts
├── tsconfig.app.json
├── nginx.conf              # nginx config used in the Docker image
├── Dockerfile
└── app/
    ├── main.ts
    ├── config.ts           # API_URL constant (reads VITE_API_URL env var)
    ├── App.vue             # Root component: auth, theme, navbar
    └── components/
        ├── GameBoard.vue       # Flag display, answer buttons, score tracking
        ├── LoginModal.vue      # Login form
        ├── SignUpModal.vue     # Registration form
        └── HighscoresModal.vue # Global leaderboard
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

## Docker

The frontend is built and served via nginx in Docker. See the root [docker-compose.yml](../../docker-compose.yml) to run the full stack.

The `VITE_API_URL` build argument controls which backend the built app points to:
```yaml
build:
  context: ./src/frontend
  args:
    VITE_API_URL: http://localhost:8000
```
