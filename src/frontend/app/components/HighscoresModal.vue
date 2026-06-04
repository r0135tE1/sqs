<template>
  <BaseModal :isOpen="isOpen" title="Top Highscores" maxWidth="32rem" @close="handleClose">
    <div v-if="loading" class="status">
      <div class="spinner"></div>
      <div class="status-muted">Loading…</div>
    </div>

    <div v-else-if="error" class="status">
      <div class="status-icon-error">⚠</div>
      <div class="status-error-text">{{ error }}</div>
    </div>

    <div v-else-if="highscores.length === 0" class="status">
      <div class="status-icon-large">🏆</div>
      <div class="status-title">No highscores yet!</div>
      <div class="status-muted">Be the first to set a record</div>
    </div>

    <div v-else class="list">
      <div class="list-header">
        <span>Player</span>
        <span>Score</span>
      </div>
      <div v-for="(entry, index) in highscores" :key="index" class="list-row">
        <div class="player">
          <div :class="['rank', rankClass(index)]">{{ index + 1 }}</div>
          <span class="player-name">{{ entry.username }}</span>
        </div>
        <span class="score">{{ entry.score }}</span>
      </div>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import { apiFetch, ApiError, NetworkError } from "../api/client";
import BaseModal from "./BaseModal.vue";

interface HighscoreEntry { username: string; score: number; }

const props = defineProps<{ isOpen: boolean; token: string | null; }>();
const emit = defineEmits(["close"]);

const loading = ref(false);
const error = ref("");
const highscores = ref<HighscoreEntry[]>([]);

function handleClose() { emit("close"); }

function rankClass(index: number) {
  if (index === 0) return "rank-gold";
  if (index === 1) return "rank-silver";
  if (index === 2) return "rank-bronze";
  return "rank-default";
}

onMounted(() => { if (props.isOpen && props.token) loadHighscores(); });
watch(() => props.isOpen, (v) => { if (v && props.token) loadHighscores(); });

async function loadHighscores() {
  if (!props.token) return;
  loading.value = true;
  error.value = "";
  try {
    highscores.value = await apiFetch<HighscoreEntry[]>("/highscores/", { token: props.token });
  } catch (err) {
    if (err instanceof NetworkError) {
      error.value = "Network error. Please check your connection.";
    } else if (err instanceof ApiError) {
      error.value = "Failed to load highscores. Please try again.";
    } else {
      error.value = "Something went wrong.";
    }
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.status { text-align: center; padding: 2.5rem 0; }
.status-title { font-weight: 500; color: var(--text); }
.status-muted { font-size: 0.875rem; color: var(--text-muted); margin-top: 0.25rem; }
.status-icon-large { font-size: 2.25rem; margin-bottom: 0.75rem; }
.status-icon-error { font-size: 1.5rem; margin-bottom: 0.5rem; color: var(--wrong); }
.status-error-text { font-size: 0.875rem; color: var(--wrong); }

.spinner {
  width: 2rem;
  height: 2rem;
  border: 4px solid var(--border);
  border-top-color: var(--primary-hover);
  border-radius: 9999px;
  margin: 0 auto 0.75rem;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.list { display: flex; flex-direction: column; gap: 0.5rem; }

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background-color: rgba(51, 65, 85, 0.6);
  color: var(--text-dim);
}

.list-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border-subtle);
  background-color: rgba(51, 65, 85, 0.4);
  transition: background-color 0.15s;
}
.list-row:hover { background-color: var(--surface-2); }

.player { display: flex; align-items: center; gap: 0.75rem; }
.player-name { font-weight: 600; font-size: 0.875rem; color: var(--text); }

.rank {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: bold;
  flex-shrink: 0;
}
.rank-gold   { background-color: #fbbf24; color: #78350f; }
.rank-silver { background-color: #94a3b8; color: #0f172a; }
.rank-bronze { background-color: #b45309; color: #fef3c7; }
.rank-default { background-color: var(--surface-3); color: var(--text-secondary); }

.score { font-weight: bold; color: var(--accent); }
</style>
