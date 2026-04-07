<script setup lang="ts">
import { onMounted, ref } from "vue";
import SignUpModal from "./components/SignUpModal.vue";

type Flag = {
  country_code: string;
  country_name: string;
  flag_url: string;
};
const showSignUp = ref(false);
const flag = ref<Flag | null>(null);
const seenCodes = ref<string[]>([]);
const guess = ref("");
const message = ref("");
const status = ref<"loading" | "ready" | "correct" | "incorrect" | "error">(
  "loading",
);
const score = ref(0);
const round = ref(0);
const apiError = ref<string | null>(null);
const animationState = ref<"none" | "success" | "failure">("none");

async function loadFlag() {
  apiError.value = null;
  message.value = "";
  status.value = "loading";

  const params = new URLSearchParams();
  seenCodes.value.forEach((code) => params.append("exclude", code));
  const url = `http://localhost:8000/flags/random${params.toString() ? `?${params.toString()}` : ""}`;

  try {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) {
      const payload = await response.json().catch(() => null);
      apiError.value =
        payload?.detail || response.statusText || "Unable to load flag.";
      status.value = "error";
      flag.value = null;
      return;
    }

    const data = (await response.json()) as Flag;
    flag.value = data;
    seenCodes.value.push(data.country_code);
    round.value += 1;
    status.value = "ready";
    guess.value = "";
  } catch (error) {
    apiError.value =
      error instanceof Error ? error.message : "Failed to fetch flag.";
    status.value = "error";
    flag.value = null;
  }
}

function checkGuess() {
  if (!flag.value) {
    return;
  }

  const normalizedGuess = guess.value.trim().toLowerCase();
  const normalizedName = flag.value.country_name.toLowerCase();

  if (normalizedGuess === normalizedName) {
    message.value = "Nice! That is correct.";
    status.value = "correct";
    score.value += 1;
    animationState.value = "success";
    setTimeout(() => {
      animationState.value = "none";
      loadFlag();
    }, 1500);
  } else {
    message.value = `Not quite. The correct answer was ${flag.value.country_name}.`;
    status.value = "incorrect";
    animationState.value = "failure";
    setTimeout(() => {
      animationState.value = "none";
      resetGame();
    }, 2000);
  }
}

function nextRound() {
  if (status.value === "loading") {
    return;
  }
  loadFlag();
}

function resetGame() {
  seenCodes.value = [];
  score.value = 0;
  round.value = 0;
  guess.value = "";
  message.value = "";
  apiError.value = null;
  loadFlag();
}

async function handleSignUp(formData : string) {
  console.log(JSON.stringify(formData));
  const response = await fetch("http://localhost:8000/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData)
  })
  if (response.ok) {
    showSignUp.value = false
  }
}

onMounted(() => {
  loadFlag();
});
</script>

<template>
  <section class="top-bar">
    <button @click="showSignUp = true">Sign Up</button>
    <button>Login</button>
  </section>

  <main class="app-shell">
    <section class="hero">
      <h1>Fun With Flags</h1>
      <p>Guess the country.</p>
    </section>

    <section class="scoreboard">
      <div><strong>Round:</strong> {{ round }}</div>
      <div><strong>Score:</strong> {{ score }}</div>
    </section>
    

  <SignUpModal
    :isOpen="showSignUp"
    @close="showSignUp = false"
    @submit="handleSignUp"
  />
    <section class="game-card">
      <div v-if="status === 'error'" class="status-message error">
        <p>Could not load a flag.</p>
        <p>{{ apiError }}</p>
        <button @click="loadFlag">Try again</button>
      </div>

      <div class="flag-preview">
        <div class="flag-canvas">
          <div v-if="status === 'loading'" class="loading-state">
            <div class="spinner" aria-hidden="true"></div>
          </div>

          <img v-else-if="flag" :src="flag.flag_url" :alt="`Flag of ${flag.country_name}`" />

          <div v-else class="empty-state">
            <span>No flag loaded yet.</span>
          </div>
          <div v-if="animationState === 'success'" class="animation-overlay success">
            <svg class="check-icon" viewBox="-1 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <path d="M19 6L9 17l-5-5" />
            </svg>
          </div>

          <div v-if="animationState === 'failure'" class="animation-overlay failure">
            <svg class="x-icon" viewBox="-1 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <path d="M17 6L6 18M6 6l12 12" />
            </svg>
          </div>
        </div>
      </div>

      <form class="guess-form" @submit.prevent="checkGuess">
        <label for="country-guess">Country name</label>
        <input id="country-guess" v-model="guess" :disabled="status === 'correct' || status === 'incorrect'"
          placeholder="Type your answer here" autocomplete="off" />

        <div class="actions">
          <button type="submit" :disabled="status === 'correct' || status === 'incorrect' || !guess.trim()
            ">
            Submit guess
          </button>
          <button type="button" @click="nextRound">Next flag</button>
          <button type="button" @click="resetGame">Reset game</button>
        </div>
      </form>

      <div v-if="message" class="feedback" :class="status">
        {{ message }}
      </div>
    </section>
  </main>
</template>

<style scoped src="./App.css"></style>
