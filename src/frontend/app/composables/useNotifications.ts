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

function add(type: NotificationType, message: string, durationMs?: number): string {
  const id =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `n-${Date.now()}-${Math.random()}`

  notifications.value.push({ id, type, message })

  const dur = durationMs ?? DEFAULT_DURATIONS[type]
  if (dur > 0) setTimeout(() => dismiss(id), dur)

  return id
}

function dismiss(id: string): void {
  notifications.value = notifications.value.filter((n) => n.id !== id)
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
