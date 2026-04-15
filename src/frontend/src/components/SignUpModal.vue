<template>
  <div v-if="isOpen" class="fixed inset-0 flex items-center justify-center z-50">
    <!-- backdrop -->
    <div class="absolute inset-0 bg-black/50 z-40" @click="$emit('close')" />
    
    <!-- modal -->
    <div class="relative bg-white rounded-xl p-8 w-full max-w-md z-50 shadow-xl border border-gray-200">
      <div class="flex justify-between items-center mb-6">
        <div class="text-2xl font-bold text-gray-800">Sign Up</div>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 text-2xl font-light cursor-pointer">×</button>
      </div>
      
      <!-- Error message display -->
      <div v-if="message" class="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
        {{ message }}
      </div>
      
      <!-- Local validation error display -->
      <div v-if="localError" class="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
        {{ localError }}
      </div>
      
      <form @submit.prevent="submit" class="flex flex-col gap-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
          <input v-model="form.username" type="text" placeholder="Choose a username" 
                 class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors" 
                 required />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
          <input v-model="form.password" type="password" placeholder="Create a password" 
                 class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors" 
                 required />
        </div>
        <button type="submit" class="w-full bg-teal-600 text-white py-3 rounded-lg hover:bg-teal-700 transition-colors font-medium mt-2">
          Create Account
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue"

const props = defineProps(["isOpen", "message"])
const emit = defineEmits(["close", "submit"])

const form = ref({
  username: "",
  password: ""
})

const localError = ref("")

// Clear local error when modal opens
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    localError.value = ""
  }
})

function close() {
  localError.value = ""
  emit("close")
}

function validateForm() {
  // Reset error
  localError.value = ""
  
  // Username validation
  if (form.value.username.length < 3) {
    localError.value = "Username must be at least 3 characters long."
    return false
  }
  
  if (!/^[a-zA-Z0-9_]+$/.test(form.value.username)) {
    localError.value = "Username can only contain letters, numbers, and underscores."
    return false
  }
  
  // Password validation
  if (form.value.password.length < 6) {
    localError.value = "Password must be at least 6 characters long."
    return false
  }
  
  if (!/\d/.test(form.value.password)) {
    localError.value = "Password must contain at least one number."
    return false
  }
  
  return true
}

function submit() {
  if (validateForm()) {
    emit("submit", form.value)
  }
}
</script>

