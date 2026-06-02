import { ref } from "vue"

export type NotificationType = "success" | "error" | "warning" | "highscore"

export interface Notification {
  id: string
  type: NotificationType
  message: string
}

const notifications = ref<Notification[]>([])

const DEFAULT_DURATIONS: Record<NotificationType, number> = {
  success: 2500,
  error: 4000,
  warning: 4000,
  highscore: 3000,
}

const dismissTimers = new Map<string, ReturnType<typeof setTimeout>>()

function scheduleDismiss(id: string, durationMs: number): void {
  if (durationMs <= 0) return
  const existing = dismissTimers.get(id)
  if (existing) clearTimeout(existing)
  dismissTimers.set(id, setTimeout(() => dismiss(id), durationMs))
}

function add(type: NotificationType, message: string, durationMs?: number): string {
  const dur = durationMs ?? DEFAULT_DURATIONS[type]

  // Dedupe: if a notification with the same type+message is already showing,
  // just reset its timer instead of stacking another one.
  const existing = notifications.value.find((n) => n.type === type && n.message === message)
  if (existing) {
    scheduleDismiss(existing.id, dur)
    return existing.id
  }

  const id =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `n-${Date.now()}-${Math.random()}`

  notifications.value.push({ id, type, message })
  scheduleDismiss(id, dur)
  return id
}

function dismiss(id: string): void {
  notifications.value = notifications.value.filter((n) => n.id !== id)
  const timer = dismissTimers.get(id)
  if (timer) {
    clearTimeout(timer)
    dismissTimers.delete(id)
  }
}

export function useNotifications() {
  return {
    notifications,
    success: (msg: string, durationMs?: number) => add("success", msg, durationMs),
    error: (msg: string, durationMs?: number) => add("error", msg, durationMs),
    warning: (msg: string, durationMs?: number) => add("warning", msg, durationMs),
    highscore: (msg: string, durationMs?: number) => add("highscore", msg, durationMs),
    dismiss,
  }
}
