<template>
  <BaseModal :isOpen="isOpen" :title="mode === 'login' ? 'Welcome Back' : 'Create Account'" @close="$emit('close')">
    <div v-if="message || localError" class="error-box">{{ message || localError }}</div>

    <form @submit.prevent="submit" class="form">
      <div>
        <label :for="`${mode}-username`" class="label">Username</label>
        <input :id="`${mode}-username`" v-model="form.username" type="text"
               :placeholder="mode === 'login' ? 'Enter your username' : 'Choose a username'"
               autocomplete="username" class="input" required />
      </div>
      <div>
        <label :for="`${mode}-password`" class="label">Password</label>
        <input :id="`${mode}-password`" v-model="form.password" type="password"
               :placeholder="mode === 'login' ? 'Enter your password' : 'Create a password'"
               :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
               class="input" required />
      </div>
      <button type="submit" :disabled="submitting" class="submit-btn">
        {{ submitting ? 'Submitting…' : (mode === 'login' ? 'Login' : 'Sign Up') }}
      </button>
    </form>
    <p class="footer">
      {{ mode === 'login' ? "Don't have an account yet?" : "Already have an account?" }}
      <button @click="$emit('switch')" class="link">{{ mode === 'login' ? 'Sign up' : 'Log in' }}</button>
    </p>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, watch } from "vue"
import BaseModal from "./BaseModal.vue"

const props = defineProps<{ isOpen: boolean; mode: "login" | "signup"; message?: string; submitting?: boolean }>()
const emit = defineEmits(["close", "submit", "switch"])

const form = ref({ username: "", password: "" })
const localError = ref("")

watch(() => props.isOpen, (v) => {
  localError.value = ""
  if (!v) form.value = { username: "", password: "" }
})

function validate() {
  if (props.mode !== "signup") return true
  localError.value = ""
  if (form.value.username.length < 3) { localError.value = "Username must be at least 3 characters long."; return false }
  if (!/^\w+$/.test(form.value.username)) { localError.value = "Username can only contain letters, numbers, and underscores."; return false }
  if (form.value.password.length < 8) { localError.value = "Password must be at least 8 characters long."; return false }
  if (!/\d/.test(form.value.password)) { localError.value = "Password must contain at least one number."; return false }
  return true
}

function submit() {
  if (props.submitting) return
  if (validate()) emit("submit", form.value)
}
</script>

<style scoped>
.error-box {
  margin-bottom: 1.25rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  border: 1px solid #be123c;
  background-color: rgba(190, 18, 60, 0.25);
  color: #FFFFFF;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.submit-btn {
  width: 100%;
  background-color: var(--primary);
  color: white;
  padding: 0.75rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  margin-top: 0.25rem;
  transition: background-color 0.15s;
}
.submit-btn:hover:not(:disabled) { background-color: #0369a1; }
.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.footer {
  text-align: center;
  font-size: 0.75rem;
  margin: 1.25rem 0 0;
  color: var(--text-muted);
}
</style>
