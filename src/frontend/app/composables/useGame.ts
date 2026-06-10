import { onMounted, ref, computed, watch, type Ref } from "vue"
import { apiFetch, ApiError, NetworkError } from "../api/client"
import { messageForError } from "../api/errors"
import { useNotifications } from "./useNotifications"

type FlagQuestion = {
  question_id: string
  flag_svg: string
  options: string[]
}

type AnswerResponse = {
  correct: boolean
  score: number
  correct_answer: string
}

export interface GameCallbacks {
  /** The current token became invalid (401) — the parent should log the user out. */
  onSessionExpired: () => void
  /** A new personal best was saved on the backend. */
  onNewHighscore: (score: number) => void
  /** The anonymous player chose to sign up from the save-score prompt. */
  onOpenSignup: () => void
  /** The anonymous player chose to log in from the save-score prompt. */
  onOpenLogin: () => void
}

/**
 * Owns the full game lifecycle — session, flag loading, answer checking,
 * scoring, personal best, and the save-score prompt — so the GameBoard
 * component stays purely presentational. All backend access goes through
 * `apiFetch`; the parent is notified of cross-cutting events via callbacks.
 */
export function useGame(token: Ref<string | null | undefined>, callbacks: GameCallbacks) {
  const notify = useNotifications()

  const flag = ref<FlagQuestion | null>(null)
  const score = ref(0)
  const sessionId = ref<string | null>(null)
  const correctAnswer = ref("")
  const showOverlay = ref(false)
  const isCorrect = ref(false)
  const selectedOption = ref("")
  const personalBest = ref<number | null>(null)
  const flagVisible = ref(true)
  const showLoginPrompt = ref(false)
  const hasShownLoginPrompt = ref(false)
  const submitting = ref(false)
  const loadFailed = ref(false)
  const reloading = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const flagDataUrl = computed(() =>
    flag.value ? `data:image/svg+xml;charset=utf-8,${encodeURIComponent(flag.value.flag_svg)}` : ""
  )

  /**
   * Centralized handler: emits session-expired on 401, shows a toast for
   * recoverable/unexpected errors. Used by the non-answer API calls.
   */
  function handleApiError(err: unknown, userMessage: string): void {
    if (err instanceof ApiError && err.status === 401) {
      callbacks.onSessionExpired()
      return
    }
    notify.error(messageForError(err, { fallback: userMessage }))
    if (!(err instanceof ApiError) && !(err instanceof NetworkError)) {
      console.error(userMessage, err)
    }
  }

  function answerBtnState(option: string) {
    if (showOverlay.value) {
      if (option === correctAnswer.value) return "correct"
      if (option === selectedOption.value) return "wrong"
      return "dimmed"
    }
    return option === selectedOption.value ? "selected" : ""
  }

  async function createSession() {
    try {
      const data = await apiFetch<{ session_id: string }>("/game/session", { method: "POST" })
      sessionId.value = data.session_id
      fetchPersonalBest()
    } catch (err) {
      handleApiError(err, "Could not start a new game.")
    }
  }

  function discardSessionState(reason?: string) {
    if (reason && score.value > 0) notify.warning(reason)
    sessionId.value = null
    score.value = 0
    selectedOption.value = ""
    showOverlay.value = false
    hasShownLoginPrompt.value = false
  }

  async function loadFlag() {
    if (!sessionId.value || reloading.value) return
    reloading.value = true
    flagVisible.value = false

    try {
      const [data] = await Promise.all([
        apiFetch<FlagQuestion>(`/game/flag?session_id=${sessionId.value}`, { cache: "no-store" }),
        new Promise((resolve) => setTimeout(resolve, 200)),
      ])
      flag.value = data
      loadFailed.value = false
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        // Session is gone (backend restart, TTL cleanup). Wipe local state so the
        // next retry creates a fresh session — otherwise we'd re-send the dead id.
        discardSessionState("Game session expired — starting over.")
      }
      flag.value = null
      loadFailed.value = true
    } finally {
      flagVisible.value = true
      reloading.value = false
    }
  }

  async function tryReload() {
    if (!sessionId.value) await createSession()
    await loadFlag()
  }

  function handleAnswerError(err: unknown) {
    // Any submit failure leaves the question in an indeterminate state — clear
    // the flag and surface the retry banner. That's a single, consistent recovery
    // path for both transient network errors and stale-session (404) cases.
    if (err instanceof ApiError && err.status === 404) {
      discardSessionState("Game session expired — starting over.")
    } else if (!(err instanceof ApiError) && !(err instanceof NetworkError)) {
      // Unexpected non-API, non-network error — log it for debugging.
      console.error("Unexpected answer error:", err)
    }
    flag.value = null
    loadFailed.value = true
    selectedOption.value = ""
  }

  async function checkInput(option: string) {
    if (!flag.value || showOverlay.value || submitting.value) return
    submitting.value = true
    selectedOption.value = option

    let result: AnswerResponse
    try {
      result = await apiFetch<AnswerResponse>("/game/answer", {
        method: "POST",
        json: { question_id: flag.value.question_id, answer: option },
      })
    } catch (err) {
      handleAnswerError(err)
      return
    } finally {
      submitting.value = false
    }

    if (result.correct) score.value = result.score
    isCorrect.value = result.correct
    correctAnswer.value = result.correct_answer

    if (!result.correct) {
      if (isAuthenticated.value && score.value > 0) saveScoreToBackend()
      if (!isAuthenticated.value && score.value > 0 && !hasShownLoginPrompt.value) {
        hasShownLoginPrompt.value = true
        showLoginPrompt.value = true
      }
    }
    showOverlay.value = true
  }

  async function fetchPersonalBest() {
    if (!token.value) return
    try {
      const data = await apiFetch<{ score: number }>("/highscores/me", { token: token.value })
      personalBest.value = data.score ?? null
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        callbacks.onSessionExpired()
        return
      }
      // 404 means "no highscore yet" — that's fine, leave personalBest as null.
      if (err instanceof ApiError && err.status === 404) return
      console.warn("Failed to fetch personal best:", err)
    }
  }

  async function nextFlag() {
    if (!isCorrect.value) score.value = 0
    showOverlay.value = false
    selectedOption.value = ""
    if (!sessionId.value) await createSession()
    loadFlag()
  }

  function openSignUpFromPrompt() {
    showLoginPrompt.value = false
    callbacks.onOpenSignup()
  }

  function openLoginFromPrompt() {
    showLoginPrompt.value = false
    callbacks.onOpenLogin()
  }

  function dismissLoginPrompt() {
    showLoginPrompt.value = false
  }

  async function saveScoreToBackend() {
    if (!token.value || !sessionId.value) return
    try {
      const data = await apiFetch<{ highscore: number | null; is_new_best: boolean }>(
        "/highscores/",
        { method: "POST", token: token.value, json: { session_id: sessionId.value } },
      )
      if (data.highscore !== null) personalBest.value = data.highscore
      if (data.is_new_best && data.highscore !== null) callbacks.onNewHighscore(data.highscore)
    } catch (err) {
      handleApiError(err, "Could not save your score.")
    }
  }

  onMounted(async () => {
    await createSession()
    loadFlag()
  })

  watch(token, async (val, oldVal) => {
    if (val && !oldVal) { // login
      await saveScoreToBackend()
    } else { // logout
      personalBest.value = null
      score.value = 0
      showOverlay.value = false
      flag.value = null
      hasShownLoginPrompt.value = false
      await createSession()
      loadFlag()
    }
  })

  return {
    // state
    flag,
    score,
    correctAnswer,
    showOverlay,
    isCorrect,
    personalBest,
    flagVisible,
    showLoginPrompt,
    submitting,
    loadFailed,
    reloading,
    // computed
    isAuthenticated,
    flagDataUrl,
    // methods
    answerBtnState,
    checkInput,
    nextFlag,
    tryReload,
    openSignUpFromPrompt,
    openLoginFromPrompt,
    dismissLoginPrompt,
  }
}
