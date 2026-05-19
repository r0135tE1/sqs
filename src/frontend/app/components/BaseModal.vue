<template>
  <div v-if="isOpen" class="modal-root">
    <div class="modal-backdrop" @click="$emit('close')" />
    <div class="modal" :style="{ maxWidth }">
      <div v-if="title" class="modal-header">
        <div class="modal-title">{{ title }}</div>
        <button @click="$emit('close')" class="close-btn">×</button>
      </div>
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  isOpen: boolean
  title?: string
  maxWidth?: string
}>(), { maxWidth: "28rem" })

defineEmits(["close"])
</script>

<style scoped>
.modal-root {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 2rem 1rem;
}

.modal-backdrop {
  position: absolute;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.6);
  z-index: 40;
}

.modal {
  position: relative;
  background-color: var(--surface);
  border: 1px solid var(--border-subtle);
  border-radius: 1rem;
  padding: 2rem;
  width: 100%;
  z-index: 50;
  max-height: calc(100vh - 4rem);
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--text);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  color: var(--text-dim);
  transition: color 0.15s;
}
.close-btn:hover { color: var(--text-secondary); }
</style>
