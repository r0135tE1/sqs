<template>
  <div v-if="isOpen" class="modal-root">
    <div class="modal-backdrop" @click="$emit('close')" />
    <div
      ref="dialogRef"
      class="modal"
      :style="{ maxWidth }"
      role="dialog"
      aria-modal="true"
      :aria-labelledby="title ? titleId : undefined"
      tabindex="-1"
      @keydown.esc="$emit('close')"
      @keydown.tab="trapFocus"
    >
      <div v-if="title" class="modal-header">
        <div :id="titleId" class="modal-title">{{ title }}</div>
        <button @click="$emit('close')" class="close-btn" type="button" aria-label="Close">×</button>
      </div>
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from "vue"

const props = withDefaults(defineProps<{
  isOpen: boolean
  title?: string
  maxWidth?: string
}>(), { maxWidth: "28rem" })

defineEmits(["close"])

let modalCount = 0
const titleId = `modal-title-${++modalCount}`

const dialogRef = ref<HTMLElement | null>(null)
let previouslyFocused: HTMLElement | null = null

const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

// Move focus into the dialog when it opens and restore it to the trigger on close,
// so keyboard and screen-reader users aren't stranded outside the modal.
watch(() => props.isOpen, async (open) => {
  if (open) {
    previouslyFocused = document.activeElement as HTMLElement | null
    await nextTick()
    dialogRef.value?.focus()
  } else {
    previouslyFocused?.focus?.()
    previouslyFocused = null
  }
})

// Keep Tab/Shift+Tab cycling within the dialog (focus trap).
function trapFocus(e: KeyboardEvent) {
  const focusables = dialogRef.value?.querySelectorAll<HTMLElement>(FOCUSABLE)
  if (!focusables || focusables.length === 0) {
    e.preventDefault()
    return
  }
  const first = focusables[0]
  const last = focusables[focusables.length - 1]
  const active = document.activeElement
  if (e.shiftKey && (active === first || active === dialogRef.value)) {
    e.preventDefault()
    last?.focus()
  } else if (!e.shiftKey && active === last) {
    e.preventDefault()
    first?.focus()
  }
}
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
