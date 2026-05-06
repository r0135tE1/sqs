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
      <div v-else :class="['text-sm italic', t.textMuted]">Log in to track your high score</div>
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
        <div v-if="flag" :class="['border w-80 h-48 overflow-hidden transition-opacity duration-200', t.flagBorder, flagVisible ? 'opacity-100' : 'opacity-0']">
          <img :src="flagDataUrl" class="w-full h-full object-cover" alt="Flag" />
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
          <div class="text-center text-white px-4 w-full">
            <div class="text-2xl font-bold mb-3 flex items-center justify-center gap-2">
              <span>✓</span><span>Correct!</span>
            </div>
            <div class="text-lg mb-4 break-words">{{ correctAnswer }}</div>
            <button @click="nextFlag" class="px-6 py-2 bg-white text-emerald-700 rounded-lg font-semibold hover:bg-emerald-50 transition-colors">
              Next Flag
            </button>
          </div>
        </div>

        <!-- Wrong overlay -->
        <div v-if="showOverlay && !isCorrect"
             class="absolute inset-0 bg-rose-500/95 flex items-center justify-center animate-fade-in">
          <div class="text-center text-white px-4 w-full">
            <div class="text-2xl font-bold mb-3 flex items-center justify-center gap-2">
              <span>✗</span><span>Wrong!</span>
            </div>
            <div class="text-sm mb-1 opacity-80">Correct Answer:</div>
            <div class="text-lg font-semibold mb-4 break-words">{{ correctAnswer }}</div>
            <button @click="nextFlag" class="px-6 py-2 bg-white text-rose-700 rounded-lg font-semibold hover:bg-rose-50 transition-colors">
              Try Again
            </button>
          </div>
        </div>
      </div>

      <!-- Answer buttons -->
      <div class="grid grid-cols-2 w-full max-w-md gap-3 transition-opacity duration-200" :class="flagVisible ? 'opacity-100' : 'opacity-0'">
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

  <Teleport to="body">
    <div v-if="showLoginPrompt" class="fixed inset-0 flex items-center justify-center z-50 px-4">
      <div class="absolute inset-0 bg-black/60" @click="dismissLoginPrompt" />
      <div :class="['relative rounded-2xl p-8 w-full max-w-sm z-50 shadow-2xl border transition-colors duration-300', t.card]">
        <div :class="['text-xl font-bold mb-2', t.textPrimary]">Save your high score!</div>
        <p :class="['text-sm mb-6', t.textSecondary]">You're not logged in. Sign up to track your scores and compete on the leaderboard.</p>
        <div class="flex gap-3">
          <button @click="openSignUpFromPrompt" :class="['flex-1 py-2 rounded-lg font-medium text-sm transition-colors', t.btnPrimary]">Sign Up</button>
          <button @click="dismissLoginPrompt" :class="['flex-1 py-2 rounded-lg font-medium text-sm transition-colors', t.btnSecondary]">Continue without saving</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>


<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed, watch } from "vue";
import { API_URL } from "../config";

const emit = defineEmits<{ 'open-signup': [] }>();

type FlagQuestion = {
  question_id: string;
  flag_svg: string;
  options: string[];
};

const props = defineProps<{
  token?: string | null;
  username?: string | null;
  isDark?: boolean;
}>();

const t = computed(() => props.isDark ? {
  card:         "bg-slate-800 border-slate-700",
  stats:        "bg-slate-700/50 border-slate-600",
  textPrimary:  "text-slate-100",
  textSecondary:"text-slate-300",
  textMuted:    "text-slate-500",
  accent:       "text-sky-400",
  flagBorder:   "border-slate-600",
  gameOverBox:  "bg-slate-700 border-slate-600",
  btnPrimary:   "bg-sky-600 text-white hover:bg-sky-500",
  btnSecondary: "bg-slate-600 text-white hover:bg-slate-500",
  btnAnswer:    "bg-slate-700 border-slate-600 text-slate-100 hover:bg-sky-600 hover:border-sky-500 hover:text-white",
} : {
  card:         "bg-white border-gray-300",
  stats:        "bg-gray-100 border-gray-300",
  textPrimary:  "text-gray-900",
  textSecondary:"text-gray-700",
  textMuted:    "text-gray-500",
  accent:       "text-sky-600",
  flagBorder:   "border-gray-500",
  gameOverBox:  "bg-gray-100 border-gray-300",
  btnPrimary:   "bg-sky-600 text-white hover:bg-sky-700",
  btnSecondary: "bg-gray-200 text-gray-800 hover:bg-gray-300",
  btnAnswer:    "bg-gray-100 border-gray-300 text-gray-900 hover:bg-sky-600 hover:border-sky-600 hover:text-white",
});

const flag = ref<FlagQuestion | null>(null);
const score = ref(0);
const sessionId = ref<string | null>(null);
const correctAnswer = ref("");
const showOverlay = ref(false);
const isCorrect = ref(false);
const gameOver = ref(false);
const personalBest = ref<number | null>(null);
const flagVisible = ref(true);
const showLoginPrompt = ref(false);
const hasShownLoginPrompt = ref(false);

const isAuthenticated = computed(() => !!props.token);
const flagDataUrl = computed(() =>
  flag.value ? `data:image/svg+xml;charset=utf-8,${encodeURIComponent(flag.value.flag_svg)}` : ""
);

onMounted(async () => {
  document.addEventListener('keydown', handleKeyDown);
  if (props.token) fetchPersonalBest();
  await createSession();
  loadFlag();
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
});

watch(() => props.token, (val) => { if (val) fetchPersonalBest(); else personalBest.value = null; });

function handleKeyDown(event: KeyboardEvent) {
  if (showOverlay.value && event.key === 'Enter') nextFlag();
}

async function createSession() {
  const response = await fetch(`${API_URL}/game/session`, { method: "POST" });
  if (!response.ok) { console.error("Failed to create session:", response.statusText); return; }
  const data = await response.json();
  sessionId.value = data.session_id;
}

async function loadFlag() {
  if (!sessionId.value) return;
  flagVisible.value = false;

  const [response] = await Promise.all([
    fetch(`${API_URL}/game/flag?session_id=${sessionId.value}`, { cache: "no-store" }),
    new Promise(resolve => setTimeout(resolve, 200)),
  ]);

  if (response.status === 404) { gameOver.value = true; flagVisible.value = true; return; }
  if (!response.ok) { console.error("Failed to load flag:", response.statusText); flagVisible.value = true; return; }

  flag.value = (await response.json()) as FlagQuestion;
  flagVisible.value = true;
}

async function checkInput(option: string) {
  if (!flag.value || showOverlay.value) return;
  const prevScore = score.value;

  const response = await fetch(`${API_URL}/game/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question_id: flag.value.question_id, answer: option }),
  });
  if (!response.ok) { console.error("Failed to submit answer:", response.statusText); return; }

  const result = await response.json();
  if (result.correct) score.value = result.score;
  isCorrect.value = result.correct;
  correctAnswer.value = result.correct_answer;

  if (!result.correct) {
    if (isAuthenticated.value && prevScore > 0) saveScoreToBackend();
    if (!isAuthenticated.value && prevScore > 0 && !hasShownLoginPrompt.value) {
      hasShownLoginPrompt.value = true;
      showLoginPrompt.value = true;
    }
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

function nextFlag() {
  if (!isCorrect.value) score.value = 0;
  showOverlay.value = false;
  loadFlag();
}

function openSignUpFromPrompt() {
  showLoginPrompt.value = false;
  emit('open-signup');
}

function dismissLoginPrompt() {
  showLoginPrompt.value = false;
}

async function resetGame() {
  score.value = 0;
  gameOver.value = false;
  showOverlay.value = false;
  flag.value = null;
  await createSession();
  loadFlag();
}

async function saveScoreToBackend() {
  if (!props.token || !sessionId.value) return;
  try {
    await fetch(`${API_URL}/highscores/`, {
      method: "POST",
      headers: { "accept": "application/json", "Content-Type": "application/json", "Authorization": `Bearer ${props.token}` },
      body: JSON.stringify({ session_id: sessionId.value }),
    });
    fetchPersonalBest();
  } catch (error) { console.error("Error saving score:", error); }
}

async function saveScore() {
  if (!props.token || !sessionId.value) return;
  try {
    const response = await fetch(`${API_URL}/highscores/`, {
      method: "POST",
      headers: { "accept": "application/json", "Content-Type": "application/json", "Authorization": `Bearer ${props.token}` },
      body: JSON.stringify({ session_id: sessionId.value }),
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
