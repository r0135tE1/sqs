<template>
  <BaseModal :isOpen="isOpen" maxWidth="24rem" @close="$emit('dismiss')">
    <div class="prompt-title">Save your high score!</div>
    <p class="prompt-text">You're not logged in. Sign up to track your scores and compete on the leaderboard.</p>
    <div class="prompt-actions">
      <button @click="$emit('signup')" class="btn btn-primary prompt-action">Sign Up</button>
      <button @click="$emit('dismiss')" class="btn btn-neutral prompt-action">Continue without saving</button>
    </div>
    <p class="prompt-footer">
      Already have an account?
      <button @click="$emit('login')" class="link">Log in</button>
    </p>
  </BaseModal>
</template>

<script setup lang="ts">
import BaseModal from "./BaseModal.vue";

defineProps<{ isOpen: boolean }>();
defineEmits<{ signup: []; login: []; dismiss: [] }>();
</script>

<style scoped>
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
