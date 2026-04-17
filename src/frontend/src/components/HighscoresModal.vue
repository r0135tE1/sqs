<template>
  <div v-if="isOpen" class="fixed inset-0 flex items-center justify-center z-50 px-4 py-8">
    <div class="absolute inset-0 bg-black/60 z-40" @click="handleClose" />
    <div :class="['relative rounded-2xl p-8 w-full max-w-lg z-50 shadow-2xl border max-h-[80vh] overflow-y-auto transition-colors duration-300', t.modal]">

      <div class="flex justify-between items-center mb-6">
        <div :class="['text-2xl font-bold', t.textPrimary]">Top Highscores</div>
        <button @click="handleClose" :class="['text-2xl leading-none transition-colors cursor-pointer', t.closeBtn]">×</button>
      </div>

      <div v-if="loading" class="text-center py-10">
        <div :class="['w-8 h-8 border-4 rounded-full animate-spin mx-auto mb-3', t.spinner]"></div>
        <div :class="t.textMuted">Loading…</div>
      </div>

      <div v-else-if="error" class="text-center py-10">
        <div class="text-rose-500 text-2xl mb-2">⚠</div>
        <div class="text-rose-500 text-sm">{{ error }}</div>
      </div>

      <div v-else-if="highscores.length === 0" class="text-center py-10">
        <div class="text-4xl mb-3">🏆</div>
        <div :class="['font-medium', t.textPrimary]">No highscores yet!</div>
        <div :class="['text-sm mt-1', t.textMuted]">Be the first to set a record</div>
      </div>

      <div v-else class="space-y-2">
        <!-- Header -->
        <div :class="['flex justify-between items-center px-4 py-2 rounded-lg text-xs font-semibold uppercase tracking-wide', t.rowHeader]">
          <span>Player</span>
          <span>Score</span>
        </div>
        <!-- Rows -->
        <div v-for="(entry, index) in highscores" :key="index"
             :class="['flex justify-between items-center px-4 py-3 rounded-lg border transition-colors', t.row]">
          <div class="flex items-center gap-3">
            <div :class="['w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0', index === 0 ? 'bg-amber-400 text-amber-900' : index === 1 ? 'bg-slate-400 text-slate-900' : index === 2 ? 'bg-amber-700 text-amber-100' : t.rankBadge]">
              {{ index + 1 }}
            </div>
            <span :class="['font-semibold text-sm', t.textPrimary]">{{ entry.username }}</span>
          </div>
          <span :class="['font-bold', t.accent]">{{ entry.score }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";

interface HighscoreEntry { username: string; score: number; }

const props = defineProps<{ isOpen: boolean; token: string | null; isDark?: boolean; }>();
const emit = defineEmits(["close"]);

const t = computed(() => props.isDark ? {
  modal:      "bg-slate-800 border-slate-700",
  textPrimary:"text-slate-100",
  textMuted:  "text-slate-500",
  accent:     "text-sky-400",
  closeBtn:   "text-slate-400 hover:text-slate-200",
  spinner:    "border-slate-600 border-t-sky-500",
  rowHeader:  "bg-slate-700/60 text-slate-400",
  row:        "bg-slate-700/40 border-slate-700 hover:bg-slate-700",
  rankBadge:  "bg-slate-600 text-slate-300",
} : {
  modal:      "bg-white border-gray-300",
  textPrimary:"text-gray-900",
  textMuted:  "text-gray-500",
  accent:     "text-sky-600",
  closeBtn:   "text-gray-400 hover:text-gray-700",
  spinner:    "border-gray-300 border-t-sky-500",
  rowHeader:  "bg-gray-200 text-gray-600",
  row:        "bg-gray-50 border-gray-200 hover:bg-gray-100",
  rankBadge:  "bg-gray-300 text-gray-700",
});

const loading = ref(false);
const error = ref("");
const highscores = ref<HighscoreEntry[]>([]);

function handleClose() { emit("close"); }

onMounted(() => { if (props.isOpen && props.token) loadHighscores(); });
watch(() => props.isOpen, (v) => { if (v && props.token) loadHighscores(); });

async function loadHighscores() {
  if (!props.token) return;
  loading.value = true;
  error.value = "";
  try {
    const response = await fetch("http://localhost:8000/highscores/", {
      headers: { Authorization: `Bearer ${props.token}` },
    });
    if (response.ok) { highscores.value = await response.json(); }
    else { error.value = "Failed to load highscores. Please try again."; }
  } catch {
    error.value = "Network error. Please check your connection.";
  } finally {
    loading.value = false;
  }
}
</script>
