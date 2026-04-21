<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { API_URL } from "./config";
import SignUpModal from "./components/SignUpModal.vue";
import LoginModal from "./components/LoginModal.vue";
import HighscoresModal from "./components/HighscoresModal.vue";
import GameBoard from "./components/GameBoard.vue";

const showSignUp = ref(false);
const showLogin = ref(false);
const showHighscores = ref(false);
const signUpMessage = ref("");
const loginMessage = ref("");
const signUpSuccessMessage = ref("");
const loginSuccessMessage = ref("");
const token = ref<string | null>(null);
const username = ref<string | null>(null);
const isDark = ref(localStorage.getItem("theme") !== "light");

const t = computed(() => isDark.value ? {
  page:       "bg-slate-900",
  nav:        "bg-slate-800 border-slate-700",
  navText:    "text-slate-100",
  userText:   "text-slate-300",
  btnPrimary: "bg-sky-600 hover:bg-sky-500 text-white",
  btnGhost:   "bg-slate-700 border border-slate-600 text-slate-200 hover:bg-slate-600",
  btnLogout:  "bg-slate-700 border border-slate-600 text-slate-300 hover:bg-rose-600 hover:text-white hover:border-rose-600",
  toast:      "bg-emerald-700 text-white",
  body:       "bg-slate-900",
} : {
  page:       "bg-gray-100",
  nav:        "bg-white border-gray-300 shadow-sm",
  navText:    "text-gray-900",
  userText:   "text-gray-700",
  btnPrimary: "bg-sky-600 hover:bg-sky-700 text-white",
  btnGhost:   "bg-white border border-gray-300 text-gray-700 hover:bg-gray-50",
  btnLogout:  "bg-white border border-gray-300 text-gray-700 hover:bg-red-50 hover:text-red-600 hover:border-red-300",
  toast:      "bg-emerald-600 text-white",
  body:       "bg-gray-100",
});

function toggleTheme() {
  isDark.value = !isDark.value;
  localStorage.setItem("theme", isDark.value ? "dark" : "light");
}

onMounted(() => {
  const savedToken = localStorage.getItem("authToken");
  const savedUsername = localStorage.getItem("username");
  if (savedToken) {
    token.value = savedToken;
    username.value = savedUsername;
  }
});

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
      signUpSuccessMessage.value = "Sign up successful! You can now log in.";
      showSignUp.value = false;
      setTimeout(() => { signUpSuccessMessage.value = ""; }, 2000);
    } else {
      const error = await response.json();
      signUpMessage.value = response.status === 409
        ? "Username already taken. Please choose a different username."
        : error.detail || "Sign up failed. Please try again.";
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
      loginSuccessMessage.value = "Login successful! Welcome back!";
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

<template>
  <div :class="['min-h-screen transition-colors duration-300', t.page]">
    <div :class="['flex justify-between items-center border-b px-6 py-4', t.nav]">
      <div :class="['text-2xl flex items-center gap-2', t.navText]" style="font-family: 'Pacifico', cursive;">
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- Pole -->
          <rect x="5" y="2" width="2.5" height="28" rx="1.25" fill="#94a3b8"/>
          <!-- Ball finial -->
          <circle cx="6.25" cy="2.5" r="2.5" fill="#94a3b8"/>
          <!-- Waving flag -->
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
      <div class="flex gap-2 items-center">
        <div v-if="token" :class="['text-sm font-medium mr-2', t.userText]">{{ username }}</div>
        <button v-if="token"  :class="['px-4 py-2 rounded-lg transition-colors font-medium text-sm', t.btnPrimary]" type="button" @click="openHighscores">Highscores</button>
        <span v-if="!token" :class="['text-sm mr-1 hidden sm:inline', t.userText]">Log in to save your scores</span>
        <button v-if="!token" :class="['px-4 py-2 rounded-lg transition-colors font-medium text-sm', t.btnGhost]"    type="button" @click="openSignUp">Sign Up</button>
        <button v-if="!token" :class="['px-4 py-2 rounded-lg transition-colors font-medium text-sm', t.btnPrimary]"  type="button" @click="openLogin">Log In</button>
        <button v-if="token"  :class="['px-4 py-2 rounded-lg transition-colors font-medium text-sm', t.btnLogout]"   type="button" @click="logout">Logout</button>
        <!-- Theme toggle -->
        <button @click="toggleTheme" :class="['px-3 py-2 rounded-lg transition-colors font-medium text-sm', t.btnGhost]" type="button" :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'">
          {{ isDark ? '☀' : '🌙' }}
        </button>
      </div>
    </div>

    <div v-if="signUpSuccessMessage || loginSuccessMessage" :class="['fixed bottom-4 right-4 px-4 py-2 rounded-lg shadow-lg z-50 flex items-center gap-2 text-sm font-medium', t.toast]">
      {{ signUpSuccessMessage || loginSuccessMessage }}
      <button @click="signUpSuccessMessage = ''; loginSuccessMessage = ''" class="opacity-70 hover:opacity-100 transition-opacity">×</button>
    </div>

    <SignUpModal    :isOpen="showSignUp"    :message="signUpMessage"  :isDark="isDark" @close="closeSignUp"    @submit="handleSignUp" />
    <LoginModal     :isOpen="showLogin"     :message="loginMessage"   :isDark="isDark" @close="closeLogin"     @submit="handleLogin" />
    <HighscoresModal :isOpen="showHighscores" :token="token"          :isDark="isDark" @close="closeHighscores" />

    <div class="container mx-auto px-4 py-8">
      <GameBoard :token="token" :username="username" :isDark="isDark" />
    </div>
  </div>
</template>

<style>
  @import 'tailwindcss';

  @font-face {
    font-family: 'Pacifico';
    src: url('/fonts/pacifico.woff2') format('woff2');
    font-weight: normal;
    font-style: normal;
    font-display: swap;
  }

  body {
    margin: 0;
  }

  @keyframes fade-in {
    from { opacity: 0; transform: scale(0.95); }
    to   { opacity: 1; transform: scale(1); }
  }
  .animate-fade-in { animation: fade-in 0.3s ease-out; }
</style>
