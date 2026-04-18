<template>
  <div :class="['max-w-2xl mx-auto rounded-xl shadow-lg border p-8 transition-colors duration-300', t.card]">

    <!-- Stats bar -->
    <div :class="['flex justify-between items-center mb-8 p-4 rounded-lg border', t.stats]">
      <div v-if="isAuthenticated" :class="['font-medium flex items-center gap-1.5', t.textSecondary]">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M8 1.5 L9.5 5.5 H13.5 L10.5 8 L11.5 12 L8 9.5 L4.5 12 L5.5 8 L2.5 5.5 H6.5 Z" fill="currentColor" opacity="0.85"/>
        </svg>
        Highscore: <span :class="['font-semibold', t.accent]">{{ personalBest ?? '—' }}</span>
      </div>
      <div v-else :class="['text-sm italic', t.textMuted]">Log in to track your best score</div>
      <div :class="['font-medium', t.textSecondary]">
        Score: <span :class="['font-semibold', t.accent]">{{ score }}</span>
      </div>
    </div>

    <!-- Title -->
    <div class="text-center mb-8">
      <h1 :class="['text-3xl font-bold mb-2', t.textPrimary]">Guess the Country!</h1>
      <p :class="t.textMuted">Look at the flag and choose the correct country</p>
    </div>

    <div class="flex flex-col items-center gap-6">
      <!-- Flag -->
      <div class="relative">
        <div v-if="flag" :class="['border w-80 h-48 overflow-hidden transition-opacity duration-300', t.flagBorder, flagVisible ? 'opacity-100' : 'opacity-0']">
          <img :src="flag.flag_url" :alt="`Flag of ${flag.country_name}`" class="w-full h-full object-cover" @load="flagVisible = true" />
        </div>
        <div v-else-if="gameOver" :class="['flex border rounded-lg w-80 h-48 items-center justify-center', t.gameOverBox]">
          <div class="text-center">
            <div :class="['text-2xl font-bold mb-4', t.textPrimary]">Game Over!</div>
            <div :class="['text-lg mb-6', t.textSecondary]">Final Score: <span :class="['font-semibold', t.accent]">{{ score }}</span></div>
            <div class="flex gap-3 justify-center">
              <button @click="resetGame" :class="['px-6 py-2 rounded-lg transition-colors font-medium', t.btnPrimary]">Play Again</button>
              <button v-if="isAuthenticated" @click="saveScore" :class="['px-6 py-2 rounded-lg transition-colors font-medium', t.btnSecondary]">Save Score</button>
            </div>
          </div>
        </div>

        <!-- Correct overlay -->
        <div v-if="showOverlay && isCorrect"
             class="absolute inset-0 bg-emerald-500/95 flex items-center justify-center animate-fade-in">
          <div class="text-center text-white">
            <div class="text-4xl font-bold mb-2">✓</div>
            <div class="text-xl font-semibold mb-1">Correct!</div>
            <div class="text-lg mb-4">{{ flag?.country_name }}</div>
            <button @click="nextFlag" class="px-6 py-2 bg-white text-emerald-700 rounded-lg font-semibold hover:bg-emerald-50 transition-colors">
              Next Flag
            </button>
          </div>
        </div>

        <!-- Wrong overlay -->
        <div v-if="showOverlay && !isCorrect"
             class="absolute inset-0 bg-rose-500/95 flex items-center justify-center animate-fade-in">
          <div class="text-center text-white">
            <div class="text-4xl font-bold mb-1">✗</div>
            <div class="text-xl font-semibold mb-1">Wrong!</div>
            <div class="text-base mb-2">Score has been reset</div>
            <div class="text-lg mb-3">{{ flag?.country_name }}</div>
            <button @click="nextFlag" class="px-6 py-2 bg-white text-rose-700 rounded-lg font-semibold hover:bg-rose-50 transition-colors">
              Try Again
            </button>
          </div>
        </div>
      </div>

      <!-- Answer buttons -->
      <div class="grid grid-cols-2 w-full max-w-md gap-3 transition-opacity duration-300" :class="flagVisible ? 'opacity-100' : 'opacity-0'">
        <button
          v-for="option in flag?.options ?? []"
          :key="option"
          :disabled="showOverlay"
          @click="checkInput(option)"
          :class="['h-14 px-4 border rounded-lg transition-colors font-medium disabled:opacity-40 disabled:cursor-not-allowed text-sm flex items-center justify-center text-center overflow-hidden', t.btnAnswer]"
        >
          <span class="line-clamp-2">{{ option }}</span>
        </button>
      </div>
    </div>
  </div>
</template>


<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed, watch } from "vue";
import { API_URL } from "../config";

type Flag = {
  country_code: string;
  country_name: string;
  flag_url: string;
  options: string[];
};

const props = defineProps<{
  token?: string | null;
  username?: string | null;
  isDark?: boolean;
}>();

const t = computed(() => props.isDark ? {
  card:        "bg-slate-800 border-slate-700",
  stats:       "bg-slate-700/50 border-slate-600",
  textPrimary: "text-slate-100",
  textSecondary:"text-slate-300",
  textMuted:   "text-slate-500",
  accent:      "text-sky-400",
  flagBorder:  "border-slate-600",
  gameOverBox: "bg-slate-700 border-slate-600",
  btnPrimary:  "bg-sky-600 text-white hover:bg-sky-500",
  btnSecondary:"bg-slate-600 text-white hover:bg-slate-500",
  btnAnswer:   "bg-slate-700 border-slate-600 text-slate-100 hover:bg-sky-600 hover:border-sky-500 hover:text-white",
} : {
  card:        "bg-white border-gray-300",
  stats:       "bg-gray-100 border-gray-300",
  textPrimary: "text-gray-900",
  textSecondary:"text-gray-700",
  textMuted:   "text-gray-500",
  accent:      "text-sky-600",
  flagBorder:  "border-gray-500",
  gameOverBox: "bg-gray-100 border-gray-300",
  btnPrimary:  "bg-sky-600 text-white hover:bg-sky-700",
  btnSecondary:"bg-gray-200 text-gray-800 hover:bg-gray-300",
  btnAnswer:   "bg-gray-100 border-gray-300 text-gray-900 hover:bg-sky-600 hover:border-sky-600 hover:text-white",
});

const flag = ref<Flag | null>(null);
const score = ref(0);
const seen = new Set<string>();
const showOverlay = ref(false);
const isCorrect = ref(false);
const gameOver = ref(false);
const personalBest = ref<number | null>(null);
const flagVisible = ref(true);

const isAuthenticated = computed(() => !!props.token);

onMounted(() => {
  loadFlag();
  document.addEventListener('keydown', handleKeyDown);
  if (props.token) fetchPersonalBest();
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
});

watch(() => props.token, (val) => { if (val) fetchPersonalBest(); else personalBest.value = null; });

function handleKeyDown(event: KeyboardEvent) {
  if (showOverlay.value && event.key === 'Enter') nextFlag();
}

async function loadFlag() {
  flagVisible.value = false;
  const params = [...seen].map(code => `exclude=${code}`).join("&");
  const response = await fetch(`${API_URL}/flags/random?${params}`, { cache: "no-store" });

  if (response.status === 404) { gameOver.value = true; flagVisible.value = true; return; }
  if (!response.ok) { console.error("Failed to load flag:", response.statusText); flagVisible.value = true; return; }

  const data = (await response.json()) as Flag;
  flag.value = data;
  seen.add(flag.value.country_code);
}

function checkInput(option: string) {
  if (!flag.value || showOverlay.value) return;
  if (option === flag.value.country_name) {
    score.value++;
    isCorrect.value = true;
  } else {
    if (score.value > 0 && (personalBest.value === null || score.value > personalBest.value)) {
      saveScoreToBackend(score.value);
    }
    score.value = 0;
    isCorrect.value = false;
  }
  showOverlay.value = true;
}

async function fetchPersonalBest() {
  if (!props.token || !props.username) return;
  try {
    const res = await fetch(`${API_URL}/highscores/`, {
      headers: { Authorization: `Bearer ${props.token}` },
    });
    if (!res.ok) return;
    const list: { username: string; score: number }[] = await res.json();
    const entry = list.find(e => e.username === props.username);
    if (entry) personalBest.value = entry.score;
  } catch (err) { console.warn("Failed to fetch personal best:", err); }
}

function nextFlag() { showOverlay.value = false; loadFlag(); }

function resetGame() {
  score.value = 0;
  seen.clear();
  gameOver.value = false;
  showOverlay.value = false;
  loadFlag();
}

async function saveScoreToBackend(scoreToSave: number) {
  if (!props.token) return;
  try {
    await fetch(`${API_URL}/highscores/`, {
      method: "POST",
      headers: { "accept": "application/json", "Content-Type": "application/json", "Authorization": `Bearer ${props.token}` },
      body: JSON.stringify({ score: scoreToSave }),
    });
    fetchPersonalBest();
  } catch (error) { console.error("Error saving score:", error); }
}

async function saveScore() {
  if (!props.token) return;
  try {
    const response = await fetch(`${API_URL}/highscores/`, {
      method: "POST",
      headers: { "accept": "application/json", "Content-Type": "application/json", "Authorization": `Bearer ${props.token}` },
      body: JSON.stringify({ score: score.value }),
    });
    if (response.ok) { await fetchPersonalBest(); resetGame(); }
  } catch (error) { console.error("Error saving score:", error); }
}
</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; transform: scale(0.8); }
  to   { opacity: 1; transform: scale(1); }
}
.animate-fade-in { animation: fade-in 0.5s ease-out; }
</style>
