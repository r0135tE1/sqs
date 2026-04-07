<template>
  <div v-if="isOpen" class="overlay" @click.self="close">
    <div class="modal">
      <h2>Sign Up</h2>

      <input v-model="form.username" type="text" placeholder="Username" />
      <input v-model="form.password" type="password" placeholder="Password" />

      <button @click="submit">Sign Up</button>
      <button @click="close">Cancel</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"

const props = defineProps(["isOpen"])
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

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 300px;
}
</style>