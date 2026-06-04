import { vi } from "vitest"
import { flushPromises } from "@vue/test-utils"

/**
 * Minimal Response stand-in for fetch mocks. The unknown→Response cast lives
 * here once so call sites can `return okJson(...)` without per-return casts.
 */
export const okJson = (data: unknown): Response =>
  ({ ok: true, status: 200, json: async () => data } as unknown as Response)

export const errJson = (status: number, body: unknown = {}): Response =>
  ({ ok: false, status, json: async () => body } as unknown as Response)

type Handler = (url: string, opts?: RequestInit) => Response | null

interface FetchMock {
  /** Match by url substring. */
  on(matcher: string, response: Response): void
  /** Custom predicate — return null to pass the request on to the next handler. */
  onMatching(predicate: Handler): void
  calls: () => unknown[][]
}

/**
 * URL-routed mock for `globalThis.fetch`. Handlers are checked in reverse
 * registration order, so calling `on('/x', ...)` after another `on('/x', ...)`
 * overrides the earlier response — useful for sequencing.
 */
export function makeFetchMock(): FetchMock {
  const handlers: Handler[] = []

  const mock = vi.fn(async (url: string, opts?: RequestInit): Promise<Response> => {
    for (let i = handlers.length - 1; i >= 0; i--) {
      const result = handlers[i]!(url, opts)
      if (result !== null) return result
    }
    return okJson({})
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
