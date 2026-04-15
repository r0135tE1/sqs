# Fun with Flags — Frontend

Vue 3 + TypeScript frontend for the Fun with Flags country guessing game.

## Requirements

- Node.js `^20.19.0` or `>=22.12.0`
- npm

## Dependencies

### Runtime

| Package | Version | Purpose |
|---------|---------|---------|
| `vue` | ^3.5 | UI framework |

### Dev / Build

| Package | Version | Purpose |
|---------|---------|---------|
| `vite` | ^8.0 | Build tool and dev server |
| `typescript` | ~6.0 | Type checking |
| `vue-tsc` | ^3.2 | TypeScript compiler for Vue SFCs |
| `@vitejs/plugin-vue` | ^6.0 | Vite plugin for `.vue` files |
| `@vitejs/plugin-vue-jsx` | ^5.1 | JSX support for Vue |
| `tailwindcss` | ^4.2 | Utility-first CSS framework |
| `@tailwindcss/vite` | ^4.2 | Tailwind Vite integration |
| `vite-plugin-vue-devtools` | ^8.1 | Vue DevTools integration |
| `npm-run-all2` | ^8.0 | Run multiple npm scripts in parallel |
| `@vue/tsconfig` | ^0.9 | Shared TypeScript config for Vue |
| `@tsconfig/node24` | ^24.0 | TypeScript config for Node 24 |
| `@types/node` | ^24.12 | Node.js type definitions |

## Setup

Install dependencies:

```bash
npm install
```

## Running the Dev Server

```bash
npm run dev
```

Vite starts a local dev server with hot module replacement (HMR). The terminal output will show the URL, typically `http://localhost:5173`.

> The frontend expects the backend API to be running at `http://localhost:8000`. Start the backend before using the app.

## Building for Production

```bash
npm run build
```

This runs a type check and then compiles the app into the `dist/` directory.

To preview the production build locally:

```bash
npm run preview
```
