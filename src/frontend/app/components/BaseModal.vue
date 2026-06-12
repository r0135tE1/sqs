<template>
  <dialog
    v-if="isOpen"
    ref="dialogRef"
    class="modal"
    :aria-labelledby="title ? titleId : undefined"
    @click="onBackdropClick"
    @cancel.prevent="$emit('close')"
    @close="$emit('close')"
  >
    <div class="modal-content" :style="{ maxWidth }">
      <div v-if="title" class="modal-header">
        <div :id="titleId" class="modal-title">{{ title }}</div>
        <button @click="$emit('close')" class="close-btn" type="button" aria-label="Close">×</button>
      </div>
      <slot />
    </div>
  </dialog>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref, useId, watch } from "vue"

const props = withDefaults(defineProps<{
  isOpen: boolean
  title?: string
  maxWidth?: string
}>(), { maxWidth: "28rem" })

const emit = defineEmits(["close"])

const titleId = useId()
const dialogRef = ref<HTMLDialogElement | null>(null)

// Open as a native modal so the browser handles focus trapping, the top layer,
// and the ::backdrop. Guarded with ?. so it degrades gracefully under jsdom,
// which does not implement HTMLDialogElement.showModal().
async function openAsModal() {
  await nextTick()
  dialogRef.value?.showModal?.()
}

onMounted(() => { if (props.isOpen) openAsModal() })
watch(() => props.isOpen, (open) => { if (open) openAsModal() })

// A click whose target is the dialog itself (the ::backdrop), not its content, closes it.
function onBackdropClick(e: MouseEvent) {
  if (e.target === dialogRef.value) emit("close")
}
</script>

<style scoped>
.modal {
  border: none;
  padding: 0;
  background: transparent;
  width: 100%;
  max-width: 100vw;
  max-height: calc(100vh - 4rem);
  overflow: visible;
  color: inherit;
}

.modal::backdrop {
  background-color: rgba(0, 0, 0, 0.6);
}

.modal-content {
  width: 100%;
  margin: 0 auto;
  background-color: var(--surface);
  border: 1px solid var(--border-subtle);
  border-radius: 1rem;
  padding: 2rem;
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
