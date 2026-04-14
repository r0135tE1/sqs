<template>
    <div class="max-w-2xl mx-auto bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <div class="flex justify-between items-center mb-8 p-4 bg-gray-50 rounded-lg border border-gray-100">
            <div class="text-gray-700 font-medium">Round: <span class="text-teal-600 font-semibold">{{ round }}</span></div>
            <div class="text-gray-700 font-medium">Score: <span class="text-teal-600 font-semibold">{{ score }}</span></div>
       </div>
       
       <div class="text-center mb-8">
         <h1 class="text-3xl font-bold text-gray-800 mb-2">Guess the Country!</h1>
         <p class="text-gray-600">Look at the flag and type the country name</p>
       </div>
       
       <div class="flex flex-col items-center gap-6">
        <div class="relative">
          <img v-if="flag" :src="flag.flag_url" alt="Flag" class="border border-gray-200 rounded-lg shadow-sm w-80 h-48 object-cover" />
          <div v-else-if="gameOver" class="flex border border-gray-200 rounded-lg w-80 h-48 items-center justify-center bg-gray-50">
            <div class="text-center">
              <div class="text-2xl font-bold text-gray-800 mb-4">Game Over!</div>
              <div class="text-lg text-gray-600 mb-6">Final Score: <span class="text-teal-600 font-semibold">{{ score }}</span></div>
              <div class="flex gap-3 justify-center">
                <button @click="resetGame" class="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium">Play Again</button>
                <button v-if="isAuthenticated" @click="saveScore" class="px-6 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors font-medium">Save Score</button>
              </div>
            </div>
          </div>
          <div v-else class="flex border border-gray-200 rounded-lg w-80 h-48 items-center justify-center bg-gray-50">
              <div class="text-center">
                <div class="w-8 h-8 border-4 border-gray-300 border-t-teal-500 rounded-full animate-spin mx-auto mb-2"></div>
                <div class="text-sm text-gray-600">Loading flag...</div>
              </div>
          </div>
          
          <!-- Overlay für korrekte Antwort -->
          <div v-if="showOverlay && isCorrect" 
               class="absolute inset-0 bg-green-500 bg-opacity-95 flex items-center justify-center rounded-lg animate-fade-in">
            <div class="text-center text-white">
              <div class="text-4xl font-bold mb-2">✓</div>
              <div class="text-xl font-semibold mb-1">Correct!</div>
              <div class="text-lg mb-4">{{ flag?.country_name }}</div>
              <button @click="nextFlag" class="px-6 py-2 bg-white text-green-600 rounded-lg font-semibold hover:bg-gray-50 transition-colors">
                Next Flag
              </button>
            </div>
          </div>
          
          <!-- Overlay für falsche Antwort -->
          <div v-if="showOverlay && !isCorrect"
               class="absolute inset-0 bg-red-500 bg-opacity-95 flex items-center justify-center rounded-lg animate-fade-in">
            <div class="text-center text-white">
              <div class="text-4xl font-bold mb-1">✗</div>
              <div class="text-xl font-semibold mb-1">Wrong!</div>
              <div class="text-base mb-2">Score has been reset</div>
              <div class="text-lg mb-3">{{ flag?.country_name }}</div>
              <button @click="nextFlag" class="px-6 py-2 bg-white text-red-600 rounded-lg font-semibold hover:bg-gray-50 transition-colors">
                Try Again
              </button>
            </div>
          </div>
        </div>
        
        <div class="flex w-full max-w-md gap-2">
          <input ref="guessInput" v-model="guess" type="text" placeholder="Type your guess here..."
                 :disabled="showOverlay"
                 class="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors disabled:bg-gray-100 disabled:cursor-not-allowed"
                 @keyup.enter="checkInput" />
          <button @click="checkInput" :disabled="showOverlay" class="px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium disabled:bg-gray-400 disabled:cursor-not-allowed">
            Submit
          </button>
        </div>
       </div>
    </div>
</template>


<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed } from "vue";

onMounted(() => {
  loadFlag();
  document.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
});

type Flag = {
  country_code: string;
  country_name: string;
  flag_url: string;
};

const props = defineProps<{
  token?: string | null;
}>();

const flag = ref<Flag | null>(null);
const score = ref(0);
const round = ref(0);
const guess = ref("");
const seen = new Set<string>();
const showOverlay = ref(false);
const isCorrect = ref(false);
const gameOver = ref(false);

const isAuthenticated = computed(() => !!props.token);
const guessInput = ref<HTMLInputElement | null>(null);

function handleKeyDown(event: KeyboardEvent) {
  if (showOverlay.value && event.key === 'Enter') {
    nextFlag();
  }
}

async function loadFlag() {
  const params = [...seen].map(code => `exclude=${code}`).join("&");
  const response = await fetch(`http://localhost:8000/flags/random?${params}`, { cache: "no-store" });
  
  if (response.status === 404) {
    gameOver.value = true;
    return;
  }
  
  if (!response.ok) {
    console.error("Failed to load flag:", response.statusText);
    return;
  }
  
  const data = (await response.json()) as Flag;
  flag.value = data;
  seen.add(flag.value.country_code);
  setTimeout(() => guessInput.value?.focus(), 0);
}

function checkInput() {
  if (!flag.value || showOverlay.value || !guess.value.trim()) return;
  
  const userGuess = guess.value.trim().toLowerCase();
  const correctName = flag.value.country_name.toLowerCase();
  
  if (userGuess === correctName) {
    score.value++;
    isCorrect.value = true;
  } else {
    console.log("First wrong guess, saving score:", score.value);
    saveScoreToBackend(score.value);
    score.value = 0; // Reset score on wrong answer
    isCorrect.value = false;
  }
  
  showOverlay.value = true;
  guess.value = "";
}

function nextFlag() {
  showOverlay.value = false;
  round.value++;
  loadFlag();
}

function resetGame() {
  score.value = 0;
  round.value = 0;
  guess.value = "";
  seen.clear();
  gameOver.value = false;
  showOverlay.value = false;
  loadFlag();
}

async function saveScoreToBackend(scoreToSave: number) {
  console.log("saveScoreToBackend called with score:", scoreToSave);
  if (!props.token) {
    console.log("No token available, skipping save");
    return;
  }

  try {
    console.log("Sending POST request to save score");
    const response = await fetch("http://localhost:8000/highscores/", {
      method: "POST",
      headers: {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": `Bearer ${props.token}`
      },
      body: JSON.stringify({ score: scoreToSave })
    });

    if (response.ok) {
      console.log("Score saved successfully!");
    } else {
      console.error("Failed to save score:", response.statusText);
    }
  } catch (error) {
    console.error("Error saving score:", error);
  }
}

async function saveScore() {
  if (!props.token) {
    console.error("No token available");
    return;
  }
  
  try {
    const response = await fetch("http://localhost:8000/highscores/", {
      method: "POST",
      headers: {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": `Bearer ${props.token}`
      },
      body: JSON.stringify({ score: score.value })
    });
    
    if (response.ok) {
      alert("Score saved successfully!");
      resetGame();
    } else {
      console.error("Failed to save score:", response.statusText);
    }
  } catch (error) {
    console.error("Error saving score:", error);
  }
}
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-fade-in {
  animation: fade-in 0.5s ease-out;
}
</style>