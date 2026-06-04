import { vi } from "vitest"
import { flushPromises } from "@vue/test-utils"

/** Shape for a happy-path JSON response. */
export const okJson = (data: unknown) => ({
  ok: true,
  status: 200,
  json: async () => data,
})

/** Shape for an error response with optional body. */
export const errJson = (status: number, body: unknown = {}) => ({
  ok: false,
  status,
  json: async () => body,
})

interface FetchMock {
  /** Match by url substring. */
  on(matcher: string, response: unknown): void
  /** Custom predicate — return non-null to handle the request. */
  onMatching(predicate: (url: string, opts?: RequestInit) => unknown | null): void
  calls: () => unknown[][]
}

/**
 * URL-routed mock for `globalThis.fetch`. Handlers are checked in reverse
 * registration order, so calling `on('/x', ...)` after another `on('/x', ...)`
 * overrides the earlier response — useful for sequencing.
 */
export function makeFetchMock(): FetchMock {
  const handlers: Array<(url: string, opts?: RequestInit) => unknown | null> = []

  const mock = vi.fn(async (url: string, opts?: RequestInit) => {
    for (let i = handlers.length - 1; i >= 0; i--) {
      const result = handlers[i]!(url, opts)
      if (result !== null) return result as Response
    }
    return okJson({}) as unknown as Response
  })

  globalThis.fetch = mock as unknown as typeof fetch

  return {
    on(matcher, response) {
      handlers.push((url) => (url.includes(matcher) ? response : null))
    },
    onMatching(predicate) {
      handlers.push(predicate)
    },
    calls: () => mock.mock.calls,
  }
}

/**
 * Run all pending timers and flush microtasks.
 * Use plain `flushPromises` instead when you have toast/notification timers
 * that you don't want to advance (they auto-dismiss after ~3 seconds).
 */
export async function settle(): Promise<void> {
  await vi.runAllTimersAsync()
  await flushPromises()
}
