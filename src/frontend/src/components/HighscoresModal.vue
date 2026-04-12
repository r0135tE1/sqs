<template>
  <div v-if="isOpen" class="fixed inset-0 flex items-center justify-center z-50 px-4 py-8">
    <!-- backdrop -->
    <div class="absolute inset-0 bg-black/50 z-40" @click="handleClose" />
    
    <!-- modal -->
    <div class="relative bg-white rounded-xl p-8 w-full max-w-lg z-50 shadow-xl border border-gray-200 max-h-[80vh] overflow-y-auto">
      <div class="flex justify-between items-center mb-6">
        <div class="text-2xl font-bold text-gray-800">Top Highscores</div>
        <button @click="handleClose" class="text-gray-400 hover:text-gray-600 text-2xl font-light cursor-pointer">×</button>
      </div>
      
      <div v-if="loading" class="text-center py-8">
        <div class="w-8 h-8 border-4 border-gray-300 border-t-teal-500 rounded-full animate-spin mx-auto mb-4"></div>
        <div class="text-gray-600">Loading highscores...</div>
      </div>
      
      <div v-else-if="error" class="text-center py-8">
        <div class="text-red-600 mb-2">⚠️</div>
        <div class="text-red-600">{{ error }}</div>
      </div>
      
      <div v-else-if="highscores.length === 0" class="text-center py-8">
        <div class="text-gray-400 text-4xl mb-4">🏆</div>
        <div class="text-gray-600 text-lg">No highscores yet!</div>
        <div class="text-gray-500 text-sm mt-2">Be the first to set a record</div>
      </div>
      
      <div v-else class="space-y-3">
        <div class="flex justify-between items-center p-4 bg-gray-200 rounded-lg border border-gray-200">
          <div class="flex items-center gap-3">
            <div class="flex items-center justify-center w-8 h-8 rounded-full bg-gray-300 text-gray-600 font-bold text-sm">
              #
            </div>
            <div class="font-semibold text-gray-700">Username</div>
          </div>
          <div class="text-gray-700 font-bold text-lg">Score</div>
        </div>
        <div v-for="(entry, index) in highscores" :key="index" 
             class="flex justify-between items-center p-4 bg-gray-50 rounded-lg border border-gray-100 hover:bg-gray-100 transition-colors">
          <div class="flex items-center gap-3">
            <div class="flex items-center justify-center w-8 h-8 rounded-full bg-teal-100 text-teal-700 font-bold text-sm">
              {{ index + 1 }}
            </div>
            <div class="font-semibold text-gray-800">{{ entry.username }}</div>
          </div>
          <div class="text-teal-600 font-bold text-lg">{{ entry.score }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";

interface HighscoreEntry {
  username: string;
  score: number;
}

const props = defineProps<{
  isOpen: boolean;
  token: string | null;
}>();

const emit = defineEmits(["close"]);

const loading = ref(false);
const error = ref("");
const highscores = ref<HighscoreEntry[]>([]);

function handleClose() {
  emit("close");
}

onMounted(() => {
  if (props.isOpen && props.token) {
    loadHighscores();
  }
});

watch(() => props.isOpen, (newIsOpen) => {
  console.log("HighscoresModal isOpen changed to:", newIsOpen);
  if (newIsOpen && props.token) {
    loadHighscores();
  }
});

async function loadHighscores() {
  if (!props.token) return;
  
  loading.value = true;
  error.value = "";
  
  try {
    const response = await fetch("http://localhost:8000/highscores/", {
      headers: {
        "Authorization": `Bearer ${props.token}`
      }
    });
    
    if (response.ok) {
      highscores.value = await response.json();
    } else {
      error.value = "Failed to load highscores. Please try again.";
    }
  } catch (err) {
    error.value = "Network error. Please check your connection.";
  } finally {
    loading.value = false;
  }
}
</script>