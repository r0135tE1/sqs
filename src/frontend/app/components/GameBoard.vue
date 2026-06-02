<template>
  <div class="card">
    <!-- Stats bar -->
    <div class="stats">
      <div v-if="isAuthenticated" class="stat-item">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M8 1.5 L9.5 5.5 H13.5 L10.5 8 L11.5 12 L8 9.5 L4.5 12 L5.5 8 L2.5 5.5 H6.5 Z" fill="currentColor" opacity="0.85"/>
        </svg>
        Highscore: <span class="accent">{{ personalBest ?? '—' }}</span>
      </div>
      <div v-else class="stat-empty">Log in to track your high score</div>
      <div class="stat-item">
        Score: <span class="accent">{{ score }}</span>
      </div>
    </div>

    <!-- Title -->
    <div class="title-block">
      <h1 class="title">Guess the Country!</h1>
      <p class="subtitle">Look at the flag and choose the correct country</p>
    </div>

    <div class="game">
      <!-- Skeleton -->
      <template v-if="!flag">
        <div class="skeleton-flag"></div>
        <div class="grid">
          <div v-for="i in 4" :key="i" class="skeleton-button"></div>
        </div>
      </template>

      <!-- Game content -->
      <template v-else>
        <div :class="['flag-box', flagVisible ? 'visible' : 'hidden']">
          <img :src="flagDataUrl" class="flag-img" alt="Flag" />
        </div>

        <div :class="['grid', flagVisible ? 'visible' : 'hidden']">
          <button
            v-for="option in flag.options"
            :key="option"
            :disabled="showOverlay"
            @click="checkInput(option)"
            :class="['answer-btn', answerBtnState(option)]"
          >
            <span class="answer-text">{{ option }}</span>
          </button>
        </div>

        <div v-if="showOverlay" :class="['result-strip', isCorrect ? 'correct' : 'wrong']">
          <span class="result-msg">
            {{ isCorrect ? '✓ Correct!' : `✗  ${correctAnswer}` }}
          </span>
          <button @click="nextFlag" :class="['result-btn', isCorrect ? 'correct' : 'wrong']">
            {{ isCorrect ? 'Next →' : 'Try Again →' }}
          </button>
        </div>
      </template>
    </div>
  </div>

  <BaseModal :isOpen="showLoginPrompt" maxWidth="24rem" @close="dismissLoginPrompt">
    <div class="prompt-title">Save your high score!</div>
    <p class="prompt-text">You're not logged in. Sign up to track your scores and compete on the leaderboard.</p>
    <div class="prompt-actions">
      <button @click="openSignUpFromPrompt" class="btn btn-primary prompt-action">Sign Up</button>
      <button @click="dismissLoginPrompt" class="btn btn-neutral prompt-action">Continue without saving</button>
    </div>
    <p class="prompt-footer">
      Already have an account?
      <button @click="openLoginFromPrompt" class="link">Log in</button>
    </p>
  </BaseModal>
</template>


<script setup lang="ts">
import { onMounted, ref, computed, watch } from "vue";
import { apiFetch, ApiError, NetworkError } from "../api/client";
import { useNotifications } from "../composables/useNotifications";
import BaseModal from "./BaseModal.vue";

const emit = defineEmits<{ 'open-signup': []; 'open-login': []; 'session-expired': []; 'new-highscore': [score: number] }>();
const notify = useNotifications();

/**
 * Centralized handler: emits 'session-expired' on 401, shows a toast for
 * unexpected system errors, swallows known recoverable cases. Returns whether
 * the caller should treat the error as handled.
 */
function handleApiError(err: unknown, userMessage: string): void {
  if (err instanceof ApiError && err.status === 401) {
    emit('session-expired');
    return;
  }
  if (err instanceof NetworkError) {
    notify.error("Network error — please check your connection.");
    return;
  }
  notify.error(userMessage);
  console.error(userMessage, err);
}

type FlagQuestion = {
  question_id: string;
  flag_svg: string;
  options: string[];
};

type AnswerResponse = {
  correct: boolean;
  score: number;
  correct_answer: string;
};

const props = defineProps<{
  token?: string | null;
  username?: string | null;
}>();

const flag = ref<FlagQuestion | null>(null);
const score = ref(0);
const sessionId = ref<string | null>(null);
const correctAnswer = ref("");
const showOverlay = ref(false);
const isCorrect = ref(false);
const selectedOption = ref("");
const personalBest = ref<number | null>(null);
const flagVisible = ref(true);
const showLoginPrompt = ref(false);
const hasShownLoginPrompt = ref(false);

const isAuthenticated = computed(() => !!props.token);
const flagDataUrl = computed(() =>
  flag.value ? `data:image/svg+xml;charset=utf-8,${encodeURIComponent(flag.value.flag_svg)}` : ""
);

function answerBtnState(option: string) {
  if (showOverlay.value) {
    if (option === correctAnswer.value) return "correct";
    if (option === selectedOption.value) return "wrong";
    return "dimmed";
  }
  return option === selectedOption.value ? "selected" : "";
}

onMounted(async () => {
  await createSession();
  loadFlag();
});


watch(() => props.token, async (val, oldVal) => {
  if (val && !oldVal) { //login
    await saveScoreToBackend();
  } else { //logout
    personalBest.value = null;
    score.value = 0;
    showOverlay.value = false;
    flag.value = null;
    hasShownLoginPrompt.value = false;
    await createSession();
    loadFlag();
  }
});


async function createSession() {
  try {
    const data = await apiFetch<{ session_id: string }>("/game/session", { method: "POST" });
    sessionId.value = data.session_id;
    fetchPersonalBest();
  } catch (err) {
    handleApiError(err, "Could not start a new game.");
  }
}

async function loadFlag() {
  if (!sessionId.value) return;
  flagVisible.value = false;

  try {
    const [data] = await Promise.all([
      apiFetch<FlagQuestion>(`/game/flag?session_id=${sessionId.value}`, { cache: "no-store" }),
      new Promise((resolve) => setTimeout(resolve, 200)),
    ]);
    flag.value = data;
  } catch (err) {
    handleApiError(err, "Could not load the next flag.");
  } finally {
    flagVisible.value = true;
  }
}

async function checkInput(option: string) {
  if (!flag.value || showOverlay.value) return;
  selectedOption.value = option;

  let result: AnswerResponse;
  try {
    result = await apiFetch<AnswerResponse>("/game/answer", {
      method: "POST",
      json: { question_id: flag.value.question_id, answer: option },
    });
  } catch (err) {
    handleApiError(err, "Could not submit your answer.");
    selectedOption.value = "";
    return;
  }

  if (result.correct) score.value = result.score;
  isCorrect.value = result.correct;
  correctAnswer.value = result.correct_answer;

  if (!result.correct) {
    if (isAuthenticated.value && score.value > 0) saveScoreToBackend();
    if (!isAuthenticated.value && score.value > 0 && !hasShownLoginPrompt.value) {
      hasShownLoginPrompt.value = true;
      showLoginPrompt.value = true;
    }
  }
  showOverlay.value = true;
}

async function fetchPersonalBest() {
  if (!props.token) return;
  try {
    const data = await apiFetch<{ score: number }>("/highscores/me", { token: props.token });
    personalBest.value = data.score || null;
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) {
      emit('session-expired');
      return;
    }
    // 404 means "no highscore yet" — that's fine, leave personalBest as null.
    if (err instanceof ApiError && err.status === 404) return;
    console.warn("Failed to fetch personal best:", err);
  }
}

async function nextFlag() {
  if (!isCorrect.value) score.value = 0;
  showOverlay.value = false;
  selectedOption.value = "";
  if (!sessionId.value) await createSession();
  loadFlag();
}

function openSignUpFromPrompt() {
  showLoginPrompt.value = false;
  emit('open-signup');
}

function openLoginFromPrompt() {
  showLoginPrompt.value = false;
  emit('open-login');
}

function dismissLoginPrompt() {
  showLoginPrompt.value = false;
}

async function saveScoreToBackend() {
  if (!props.token || !sessionId.value) return;
  try {
    const data = await apiFetch<{ highscore: number | null; is_new_best: boolean }>(
      "/highscores/",
      { method: "POST", token: props.token, json: { session_id: sessionId.value } },
    );
    if (data.highscore !== null) personalBest.value = data.highscore;
    if (data.is_new_best && data.highscore !== null) emit('new-highscore', data.highscore);
  } catch (err) {
    handleApiError(err, "Could not save your score.");
  }
}

</script>

<style scoped>
.card {
  max-width: 42rem;
  margin: 0 auto;
  border-radius: 0.75rem;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
  border: 1px solid var(--border-subtle);
  background-color: var(--surface);
  padding: 2rem;
}

/* Stats bar */
.stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border);
  background-color: rgba(51, 65, 85, 0.5);
}

.stat-item {
  font-weight: 500;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.stat-empty {
  font-size: 0.875rem;
  font-style: italic;
  color: var(--text-muted);
}

.accent { font-weight: 600; color: var(--accent); }

/* Title */
.title-block { text-align: center; margin-bottom: 2rem; }

.title {
  font-size: 1.875rem;
  font-weight: bold;
  margin: 0 0 0.5rem;
  color: var(--text);
}

.subtitle { color: var(--text-muted); margin: 0; }

/* Game container */
.game {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

/* Skeleton */
.skeleton-flag {
  width: 20rem;
  height: 12rem;
  border-radius: 0.25rem;
  background-color: var(--surface-2);
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.skeleton-button {
  height: 3.5rem;
  border-radius: 0.5rem;
  background-color: var(--surface-2);
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Flag */
.flag-box {
  width: 20rem;
  height: 12rem;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: opacity 0.2s;
}
.flag-box.visible { opacity: 1; }
.flag-box.hidden { opacity: 0; }

.flag-img { max-width: 100%; max-height: 100%; }

/* Answer buttons grid */
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  width: 100%;
  max-width: 28rem;
  gap: 0.75rem;
  transition: opacity 0.2s;
}
.grid.visible { opacity: 1; }
.grid.hidden { opacity: 0; }

.answer-btn {
  height: 3.5rem;
  padding: 0 1rem;
  border: 1px solid var(--border);
  background-color: var(--surface-2);
  color: var(--text);
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  overflow: hidden;
  transition: background-color 0.15s, border-color 0.15s, color 0.15s;
}
.answer-btn:hover:not(:disabled) {
  background-color: var(--primary);
  border-color: var(--primary-hover);
  color: white;
}

.answer-btn.selected {
  background-color: var(--primary-deep);
  border-color: var(--primary);
  color: var(--text);
  cursor: default;
}

.answer-btn.correct {
  background-color: var(--correct);
  border-color: var(--correct);
  color: white;
  cursor: default;
}

.answer-btn.wrong {
  background-color: var(--wrong);
  border-color: var(--wrong);
  color: white;
  cursor: default;
}

.answer-btn.dimmed {
  background-color: rgba(51, 65, 85, 0.5);
  border-color: var(--border-subtle);
  color: var(--text-muted);
  cursor: default;
}

.answer-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Result strip */
.result-strip {
  width: 100%;
  max-width: 28rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  animation: fade-in 0.5s ease-out;
}
.result-strip.correct { background-color: rgba(16, 185, 129, 0.1); }
.result-strip.wrong   { background-color: rgba(244, 63, 94, 0.1); }

.result-msg { font-weight: 500; font-size: 0.875rem; }
.result-strip.correct .result-msg { color: var(--correct); }
.result-strip.wrong   .result-msg { color: var(--text-secondary); }

.result-btn {
  padding: 0.375rem 1rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
  transition: background-color 0.15s;
}
.result-btn.correct { background-color: var(--correct); }
.result-btn.correct:hover { background-color: var(--correct-hover); }
.result-btn.wrong   { background-color: var(--wrong); }
.result-btn.wrong:hover   { background-color: var(--wrong-hover); }

@keyframes fade-in {
  from { opacity: 0; transform: scale(0.8); }
  to   { opacity: 1; transform: scale(1); }
}

/* Login prompt */
.prompt-title {
  font-size: 1.25rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: var(--text);
}

.prompt-text {
  font-size: 0.875rem;
  margin: 0 0 1.5rem;
  color: var(--text-secondary);
}

.prompt-actions {
  display: flex;
  gap: 0.75rem;
}

.prompt-action { flex: 1; }

.prompt-footer {
  text-align: center;
  font-size: 0.75rem;
  margin: 1rem 0 0;
  color: var(--text-muted);
}
</style>
