<template>
  <div class="page">
    <nav class="nav">
      <div class="brand">
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="5" y="2" width="2.5" height="28" rx="1.25" fill="#94a3b8"/>
          <circle cx="6.25" cy="2.5" r="2.5" fill="#94a3b8"/>
          <path d="M7.5 5 C12 3 20 7 26 4.5 C20 9 12 7 7.5 10 Z" fill="url(#stripe1)"/>
          <path d="M7.5 10 C12 7 20 11 26 8.5 C20 13 12 11 7.5 14 Z" fill="white" opacity="0.9"/>
          <path d="M7.5 14 C12 11 20 15 26 12.5 C20 17 12 15 7.5 18 Z" fill="url(#stripe3)"/>
          <defs>
            <linearGradient id="stripe1" x1="7" y1="4" x2="26" y2="8" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stop-color="#f97316"/>
              <stop offset="100%" stop-color="#ef4444"/>
            </linearGradient>
            <linearGradient id="stripe3" x1="7" y1="13" x2="26" y2="16" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stop-color="#3b82f6"/>
              <stop offset="100%" stop-color="#6366f1"/>
            </linearGradient>
          </defs>
        </svg>
        Fun With Flags
      </div>
      <div class="nav-actions">
        <div v-if="token" class="username">{{ username }}</div>
        <button v-if="token"  class="btn btn-primary" type="button" @click="openHighscores">Highscores</button>
        <span v-if="!token" class="login-hint">Log in to save your scores</span>
        <button v-if="!token" class="btn btn-ghost"   type="button" @click="openSignUp">Sign Up</button>
        <button v-if="!token" class="btn btn-primary" type="button" @click="openLogin">Log In</button>
        <button v-if="token"  class="btn btn-logout"  type="button" @click="logout">Logout</button>
      </div>
    </nav>

    <NotificationStack />

    <AuthModal :isOpen="showSignUp" mode="signup" :message="signUpMessage" :submitting="signUpSubmitting" @close="closeSignUp" @submit="handleSignUp" @switch="closeSignUp(); openLogin()" />
    <AuthModal :isOpen="showLogin"  mode="login"  :message="loginMessage"  :submitting="loginSubmitting"  @close="closeLogin"  @submit="handleLogin"  @switch="closeLogin(); openSignUp()" />
    <HighscoresModal :isOpen="showHighscores" :token="token" @close="closeHighscores" />

    <main class="content">
      <ErrorBoundary>
        <GameBoard :token="token" :username="username" @open-signup="openSignUp" @open-login="openLogin" @session-expired="handleSessionExpired" @new-highscore="handleNewHighscore" />
      </ErrorBoundary>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

import { apiFetch, ApiError, NetworkError } from "./api/client";
import { useNotifications } from "./composables/useNotifications";
import AuthModal from "./components/AuthModal.vue";
import HighscoresModal from "./components/HighscoresModal.vue";
import GameBoard from "./components/GameBoard.vue";
import NotificationStack from "./components/NotificationStack.vue";
import ErrorBoundary from "./components/ErrorBoundary.vue";

const showSignUp = ref(false);
const showLogin = ref(false);
const showHighscores = ref(false);
const signUpMessage = ref("");
const loginMessage = ref("");
const signUpSubmitting = ref(false);
const loginSubmitting = ref(false);
const token = ref<string | null>(localStorage.getItem("authToken"));
const username = ref<string | null>(localStorage.getItem("username"));

const notify = useNotifications();

function openSignUp() { signUpMessage.value = ""; showSignUp.value = true; }
function closeSignUp() { showSignUp.value = false; }
function openLogin()  { loginMessage.value = ""; showLogin.value = true; }
function closeLogin() { showLogin.value = false; }
function closeHighscores() { showHighscores.value = false; }
function openHighscores()  { showHighscores.value = true; }

function logout() {
  token.value = null;
  username.value = null;
  localStorage.removeItem("authToken");
  localStorage.removeItem("username");
  loginMessage.value = signUpMessage.value = "";
}

function handleSessionExpired() {
  logout();
  notify.warning("Session expired — please log in again.");
}

function handleNewHighscore(score: number) {
  notify.highscore(`🎉 New high score: ${score}!`);
}

/**
 * Errors from auth endpoints belong INLINE in the form (the user is looking
 * right at it). System-level errors (network, 5xx) get a toast on top.
 */
function describeAuthError(err: unknown, conflictMsg: string, fallbackMsg: string): string {
  if (err instanceof NetworkError) return "Network error. Please check your connection and try again.";
  if (err instanceof ApiError) {
    if (err.status === 409) return conflictMsg;
    if (err.status === 401) return "Invalid username or password. Please try again.";
    return err.detail || fallbackMsg;
  }
  return fallbackMsg;
}

async function handleSignUp(formData: { username: string; password: string }) {
  if (signUpSubmitting.value) return;
  signUpSubmitting.value = true;
  signUpMessage.value = "";
  try {
    await apiFetch("/auth/register", { method: "POST", json: formData });
    showSignUp.value = false;
    await handleLogin(formData);
  } catch (err) {
    signUpMessage.value = describeAuthError(
      err,
      "Username already taken. Please choose a different username.",
      "Sign up failed. Please try again.",
    );
  } finally {
    signUpSubmitting.value = false;
  }
}

async function handleLogin(formData: { username: string; password: string }) {
  if (loginSubmitting.value) return;
  loginSubmitting.value = true;
  loginMessage.value = "";
  try {
    const data = await apiFetch<{ access_token: string }>("/auth/login", {
      method: "POST",
      json: formData,
    });
    token.value = data.access_token;
    username.value = formData.username;
    localStorage.setItem("authToken", data.access_token);
    localStorage.setItem("username", formData.username);
    notify.success("Login successful! Welcome!");
    showLogin.value = false;
  } catch (err) {
    loginMessage.value = describeAuthError(
      err,
      "",
      "Login failed. Please try again.",
    );
  } finally {
    loginSubmitting.value = false;
  }
}
</script>

<style>
  :root {
    --bg: #0f172a;
    --surface: #1e293b;
    --surface-2: #334155;
    --surface-3: #475569;
    --border: #475569;
    --border-subtle: #334155;
    --text: #f1f5f9;
    --text-secondary: #cbd5e1;
    --text-muted: #64748b;
    --text-dim: #94a3b8;
    --accent: #38bdf8;
    --primary: #0284c7;
    --primary-hover: #0ea5e9;
    --primary-deep: #0c4a6e;
    --correct: #10b981;
    --correct-hover: #059669;
    --wrong: #f43f5e;
    --wrong-hover: #e11d48;
    --warning: #d97706;
  }

  @font-face {
    font-family: 'Pacifico';
    src: url('/fonts/pacifico.woff2') format('woff2');
    font-weight: normal;
    font-style: normal;
    font-display: swap;
  }

  *, *::before, *::after { box-sizing: border-box; }

  body {
    margin: 0;
    background-color: var(--bg);
    color: var(--text);
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.5;
  }

  button { font: inherit; cursor: pointer; }

  #app {
    animation: app-enter 0.25s ease-out;
  }

  @keyframes app-enter {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  /* Shared utility classes */
  .btn {
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    font-weight: 500;
    font-size: 0.875rem;
    border: 1px solid transparent;
    transition: background-color 0.15s, color 0.15s, border-color 0.15s;
  }
  .btn-primary {
    background-color: var(--primary);
    color: white;
  }
  .btn-primary:hover { background-color: var(--primary-hover); }

  .btn-ghost {
    background-color: var(--surface-2);
    border-color: var(--border);
    color: var(--text-secondary);
  }
  .btn-ghost:hover { background-color: var(--surface-3); }

  .btn-neutral {
    background-color: var(--surface-3);
    color: var(--text);
  }
  .btn-neutral:hover { background-color: #64748b; }

  .btn-logout {
    background-color: var(--surface-2);
    border-color: var(--border);
    color: var(--text-secondary);
  }
  .btn-logout:hover {
    background-color: var(--wrong);
    color: white;
    border-color: var(--wrong);
  }

  .link {
    background: none;
    border: none;
    padding: 0;
    color: var(--accent);
    text-decoration: underline;
    transition: opacity 0.15s;
    cursor: pointer;
  }
  .link:hover { opacity: 0.8; }

  .label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 0.375rem;
    color: var(--text-secondary);
  }

  .input {
    width: 100%;
    border-radius: 0.5rem;
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
    border: 1px solid var(--border);
    background-color: var(--surface-2);
    color: var(--text);
    outline: none;
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  .input::placeholder { color: var(--text-muted); }
  .input:focus {
    border-color: transparent;
    box-shadow: 0 0 0 2px var(--primary-hover);
  }
</style>

<style scoped>
  .page {
    min-height: 100vh;
    background-color: var(--bg);
  }

  .nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-subtle);
    background-color: var(--surface);
    padding: 1rem 1.5rem;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.5rem;
    color: var(--text);
    font-family: 'Pacifico', cursive;
  }

  .nav-actions {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .username {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-secondary);
    margin-right: 0.5rem;
  }

  .login-hint {
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-right: 0.25rem;
  }
  @media (max-width: 640px) {
    .login-hint { display: none; }
  }

  .content {
    max-width: 1280px;
    margin: 0 auto;
    padding: 2rem 1rem;
  }
</style>
