<template>
  <div v-if="isOpen" class="fixed inset-0 flex items-center justify-center z-50">
    <!-- backdrop -->
    <div class="absolute inset-0 bg-black/50 z-40" @click="$emit('close')" />
    
    <!-- modal -->
    <div class="relative bg-white rounded-xl p-8 w-full max-w-md z-50 shadow-xl border border-gray-200">
      <div class="flex justify-between items-center mb-6">
        <div class="text-2xl font-bold text-gray-800">Login</div>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 text-2xl font-light cursor-pointer">×</button>
      </div>
      
      <!-- Error message display -->
      <div v-if="message" class="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
        {{ message }}
      </div>
      
      <form @submit.prevent="submit" class="flex flex-col gap-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
          <input v-model="form.username" type="text" placeholder="Enter your username" 
                 class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors" 
                 required />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
          <input v-model="form.password" type="password" placeholder="Enter your password" 
                 class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors" 
                 required />
        </div>
        <button type="submit" class="w-full bg-teal-600 text-white py-3 rounded-lg hover:bg-teal-700 transition-colors font-medium mt-2">
          Login
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"

const props = defineProps(["isOpen", "message"])
const emit = defineEmits(["close", "submit"])

const form = ref({
  username: "",
  password: ""
})

function close() {
  emit("close")
}

function submit() {
  emit("submit", form.value)
}
</script>

