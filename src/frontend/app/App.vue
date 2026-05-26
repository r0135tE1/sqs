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

    <div v-if="signUpSuccessMessage || loginSuccessMessage" class="toast toast-success">
      {{ signUpSuccessMessage || loginSuccessMessage }}
      <button @click="signUpSuccessMessage = ''; loginSuccessMessage = ''" class="toast-close">×</button>
    </div>

    <div v-if="sessionExpiredMessage" class="toast toast-warning">
      {{ sessionExpiredMessage }}
      <button @click="sessionExpiredMessage = ''" class="toast-close">×</button>
    </div>

    <div v-if="newHighscoreMessage" class="toast-highscore-banner">
      {{ newHighscoreMessage }}
      <button @click="newHighscoreMessage = ''" class="toast-close">×</button>
    </div>

    <AuthModal :isOpen="showSignUp" mode="signup" :message="signUpMessage" @close="closeSignUp" @submit="handleSignUp" @switch="closeSignUp(); openLogin()" />
    <AuthModal :isOpen="showLogin"  mode="login"  :message="loginMessage"  @close="closeLogin"  @submit="handleLogin"  @switch="closeLogin(); openSignUp()" />
    <HighscoresModal :isOpen="showHighscores" :token="token" @close="closeHighscores" />

    <main class="content">
      <GameBoard :token="token" :username="username" @open-signup="openSignUp" @open-login="openLogin" @session-expired="handleSessionExpired" @new-highscore="handleNewHighscore" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

import { API_URL } from "./config";
import AuthModal from "./components/AuthModal.vue";
import HighscoresModal from "./components/HighscoresModal.vue";
import GameBoard from "./components/GameBoard.vue";

const showSignUp = ref(false);
const showLogin = ref(false);
const showHighscores = ref(false);
const signUpMessage = ref("");
const loginMessage = ref("");
const signUpSuccessMessage = ref("");
const loginSuccessMessage = ref("");
const sessionExpiredMessage = ref("");
const newHighscoreMessage = ref("");
const token = ref<string | null>(localStorage.getItem("authToken"));
const username = ref<string | null>(localStorage.getItem("username"));

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
  loginMessage.value = signUpMessage.value = loginSuccessMessage.value = signUpSuccessMessage.value = "";
}

function handleSessionExpired() {
  logout();
  sessionExpiredMessage.value = "Session expired — please log in again.";
  setTimeout(() => { sessionExpiredMessage.value = ""; }, 4000);
}

function handleNewHighscore(score: number) {
  newHighscoreMessage.value = `🎉 New high score: ${score}!`;
  setTimeout(() => { newHighscoreMessage.value = ""; }, 3000);
}

async function handleSignUp(formData: { username: string; password: string }) {
  signUpMessage.value = "";
  signUpSuccessMessage.value = "";
  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: "POST",
      headers: { "accept": "application/json", "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    if (response.ok) {
      showSignUp.value = false;
      await handleLogin(formData);
    } else {
      const error = await response.json();
      const detail = typeof error.detail === "string" ? error.detail : null;
      signUpMessage.value = response.status === 409
        ? "Username already taken. Please choose a different username."
        : detail ?? "Sign up failed. Please try again.";
    }
  } catch {
    signUpMessage.value = "Network error. Please check your connection and try again.";
  }
}

async function handleLogin(formData: { username: string; password: string }) {
  loginMessage.value = "";
  loginSuccessMessage.value = "";
  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "accept": "application/json", "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    if (response.ok) {
      const data = await response.json();
      token.value = data.access_token;
      username.value = formData.username;
      localStorage.setItem("authToken", data.access_token);
      localStorage.setItem("username", formData.username);
      loginSuccessMessage.value = "Login successful! Welcome!";
      showLogin.value = false;
      setTimeout(() => { loginSuccessMessage.value = ""; }, 2000);
    } else {
      const error = await response.json();
      loginMessage.value = response.status === 401
        ? "Invalid username or password. Please try again."
        : error.detail || "Login failed. Please try again.";
    }
  } catch {
    loginMessage.value = "Network error. Please check your connection and try again.";
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

  .toast {
    position: fixed;
    bottom: 1rem;
    right: 1rem;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.4);
    z-index: 50;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: white;
  }
  .toast-success { background-color: #047857; }
  .toast-warning { background-color: var(--warning); }

  .toast-highscore-banner {
    position: fixed;
    top: 5.5rem;
    left: 50%;
    transform: translateX(-50%);
    padding: 0.875rem 1.5rem;
    border-radius: 0.75rem;
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
    z-index: 50;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1rem;
    font-weight: 600;
    color: white;
    background-color: var(--primary);
    animation: highscore-pop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  @keyframes highscore-pop {
    0%   { opacity: 0; transform: translate(-50%, -1rem) scale(0.9); }
    100% { opacity: 1; transform: translate(-50%, 0) scale(1); }
  }
  .toast-close {
    background: none;
    border: none;
    color: white;
    opacity: 0.7;
    transition: opacity 0.15s;
  }
  .toast-close:hover { opacity: 1; }

  .content {
    max-width: 1280px;
    margin: 0 auto;
    padding: 2rem 1rem;
  }
</style>
