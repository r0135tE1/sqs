<template>
  <div class="stack-bottom-right">
    <div
      v-for="n in bottomNotifications"
      :key="n.id"
      :class="['toast', `toast-${n.type}`]"
    >
      {{ n.message }}
      <button @click="dismiss(n.id)" class="toast-close" aria-label="Dismiss">×</button>
    </div>
  </div>

  <div class="stack-top-center">
    <div
      v-for="n in topNotifications"
      :key="n.id"
      class="toast-highscore-banner"
    >
      {{ n.message }}
      <button @click="dismiss(n.id)" class="toast-close" aria-label="Dismiss">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue"
import { useNotifications } from "../composables/useNotifications"

const { notifications, dismiss } = useNotifications()

const topNotifications = computed(() =>
  notifications.value.filter((n) => n.type === "highscore"),
)

const bottomNotifications = computed(() =>
  notifications.value.filter((n) => n.type !== "highscore"),
)
</script>

<style scoped>
.stack-bottom-right {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  z-index: 50;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-end;
}

.stack-top-center {
  position: fixed;
  top: 5.5rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 50;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
}

.toast {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  animation: slide-in 0.2s ease-out;
}

.toast-success { background-color: #047857; }
.toast-error   { background-color: var(--wrong); }
.toast-warning { background-color: var(--warning); }

.toast-highscore-banner {
  padding: 0.875rem 1.5rem;
  border-radius: 0.75rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  background-color: var(--primary);
  animation: highscore-pop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.toast-close {
  background: none;
  border: none;
  color: white;
  opacity: 0.7;
  transition: opacity 0.15s;
}
.toast-close:hover { opacity: 1; }

@keyframes slide-in {
  from { opacity: 0; transform: translateX(0.5rem); }
  to   { opacity: 1; transform: translateX(0); }
}

@keyframes highscore-pop {
  0%   { opacity: 0; transform: translateY(-1rem) scale(0.9); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}
</style>
