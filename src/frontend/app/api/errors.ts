import { ApiError, NetworkError } from "./client"

const DEFAULT_NETWORK = "Network error. Please check your connection."
const DEFAULT_FALLBACK = "Something went wrong. Please try again."

export interface ErrorMessageOptions {
  /** Message for a connection failure (NetworkError). */
  network?: string
  /** Message for an HTTP 409 conflict (e.g. username taken). */
  conflict?: string
  /** Message for an HTTP 401 unauthorized. */
  unauthorized?: string
  /** Fixed message for any other ApiError, overriding the backend `detail`. */
  api?: string
  /** Message for an unknown error, and the last resort for an ApiError without detail. */
  fallback?: string
}

/**
 * Maps an unknown thrown error to a user-facing message. Centralizes the
 * NetworkError / ApiError / unknown branching that the views otherwise repeat.
 */
export function messageForError(err: unknown, options: ErrorMessageOptions = {}): string {
  const fallback = options.fallback ?? DEFAULT_FALLBACK
  if (err instanceof NetworkError) return options.network ?? DEFAULT_NETWORK
  if (err instanceof ApiError) {
    if (err.status === 409 && options.conflict) return options.conflict
    if (err.status === 401 && options.unauthorized) return options.unauthorized
    if (options.api) return options.api
    return err.detail || fallback
  }
  return fallback
}
