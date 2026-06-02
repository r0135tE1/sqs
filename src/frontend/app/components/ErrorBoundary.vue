<template>
  <div v-if="error" class="error-fallback">
    <div class="error-card">
      <h2 class="error-title">Something went wrong</h2>
      <p class="error-text">An unexpected error occurred. You can try to reload this section.</p>
      <button @click="reset" class="btn btn-primary">Try again</button>
    </div>
  </div>
  <slot v-else />
</template>

<script setup lang="ts">
import { onErrorCaptured, ref } from "vue"

const error = ref<Error | null>(null)

onErrorCaptured((err) => {
  error.value = err as Error
  console.error("Component error captured:", err)
  return false
})

function reset() {
  error.value = null
}
</script>

<style scoped>
.error-fallback {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.error-card {
  background-color: var(--surface);
  border: 1px solid var(--border-subtle);
  border-radius: 0.75rem;
  padding: 2rem;
  text-align: center;
  max-width: 28rem;
}

.error-title {
  font-size: 1.25rem;
  font-weight: bold;
  color: var(--text);
  margin: 0 0 0.5rem;
}

.error-text {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0 0 1.5rem;
}
</style>
