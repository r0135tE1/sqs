<script setup lang="ts">
import { onMounted, ref } from "vue";
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

// Load token from localStorage on mount
onMounted(() => {
  const savedToken = localStorage.getItem("authToken");
  const savedUsername = localStorage.getItem("username");
  if (savedToken) {
    token.value = savedToken;
    username.value = savedUsername;
  }
});

function openSignUp() {
  signUpMessage.value = "";
  showSignUp.value = true;
}

function closeSignUp() {
  showSignUp.value = false;
}

function openLogin() {
  loginMessage.value = "";
  showLogin.value = true;
}

function closeLogin() {
  showLogin.value = false;
}

function closeHighscores() {
  showHighscores.value = false;
}

function openHighscores() {
  console.log("Highscores button clicked");
  showHighscores.value = true;
}

function logout() {
  token.value = null;
  username.value = null;
  localStorage.removeItem("authToken");
  localStorage.removeItem("username");
  loginMessage.value = "";
  signUpMessage.value = "";
  loginSuccessMessage.value = "";
  signUpSuccessMessage.value = "";
}

async function handleSignUp(formData : { username: string; password: string }) {
  signUpMessage.value = "";
  signUpSuccessMessage.value = "";
  
  try {
    const response = await fetch("http://localhost:8000/auth/register", {
      method: "POST",
      headers: { 
        "accept": "application/json",
        "Content-Type": "application/json" },
      body: JSON.stringify(formData)
    });
    
    if (response.ok) {
      signUpSuccessMessage.value = "Sign up successful! You can now log in.";
      showSignUp.value = false;
    } else {
      const error = await response.json();
      if (response.status === 409) {
        signUpMessage.value = "Username already taken. Please choose a different username.";
      } else {
        signUpMessage.value = error.detail || "Sign up failed. Please try again.";
      }
    }
  } catch (error) {
    console.error("Sign up error:", error);
    signUpMessage.value = "Network error. Please check your connection and try again.";
  }
}

async function handleLogin(formData : { username: string; password: string }) {
  loginMessage.value = "";
  loginSuccessMessage.value = "";
  
  try {
    const response = await fetch("http://localhost:8000/auth/login", {
      method: "POST",
      headers: { 
        "accept": "application/json",
        "Content-Type": "application/json" },
      body: JSON.stringify(formData)
    });
    
    if (response.ok) {
      const data = await response.json();
      token.value = data.access_token;
      username.value = formData.username;
      localStorage.setItem("authToken", data.access_token);
      localStorage.setItem("username", formData.username);
      loginSuccessMessage.value = "Login successful! Welcome back!";
      showLogin.value = false;
    } else {
      const error = await response.json();
      if (response.status === 401) {
        loginMessage.value = "Invalid username or password. Please try again.";
      } else {
        loginMessage.value = error.detail || "Login failed. Please try again.";
      }
    }
  } catch (error) {
    console.error("Login error:", error);
    loginMessage.value = "Network error. Please check your connection and try again.";
  }
}
</script>



<template>
  <div class="min-h-screen bg-gray-50">
    <div class="flex justify-between items-center bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div class="text-gray-800 text-2xl font-semibold">Fun With Flags</div>
      <div class="flex gap-3 items-center">
        <div v-if="token" class="text-sm text-gray-600 font-medium mr-4">{{ username }}</div>
        <button v-if="token" class="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium" type="button" @click="openHighscores">Highscores</button>
        <button v-if="!token" class="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors font-medium" type="button" @click="openSignUp">Sign Up</button>
        <button v-if="!token" class="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors font-medium" type="button" @click="openLogin">Login</button>
        <button v-if="token" class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-medium" type="button" @click="logout">Logout</button>
      </div>
   </div>
   
   <!-- Success message display -->
   <div v-if="signUpSuccessMessage" class="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50">
     {{ signUpSuccessMessage }}
     <button @click="signUpSuccessMessage = ''" class="ml-2 font-bold hover:bg-green-600 rounded px-1 cursor-pointer">×</button>
   </div>
   
   <!-- Login success message display -->
   <div v-if="loginSuccessMessage" class="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50">
     {{ loginSuccessMessage }}
     <button @click="loginSuccessMessage = ''" class="ml-2 font-bold hover:bg-green-600 rounded px-1 cursor-pointer">×</button>
   </div>
   
   <SignUpModal :isOpen="showSignUp" :message="signUpMessage" @close="closeSignUp" @submit="handleSignUp" />
   <LoginModal :isOpen="showLogin" :message="loginMessage" @close="closeLogin" @submit="handleLogin"/>
   <HighscoresModal :isOpen="showHighscores" :token="token" @close="closeHighscores" />
   <div class="container mx-auto px-4 py-8">
     <GameBoard :token="token" />
   </div>
  </div>
</template>

<style>
  @import 'tailwindcss';
  
  @keyframes fade-in {
    from {
      opacity: 0;
      transform: scale(0.95);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }
  
  .animate-fade-in {
    animation: fade-in 0.3s ease-out;
  }
</style>