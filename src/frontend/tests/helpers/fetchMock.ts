import { vi } from "vitest"
import { flushPromises, type VueWrapper, type DOMWrapper } from "@vue/test-utils"

type FetchHandler = (url: string, opts?: RequestInit) => Promise<Response>
type RoutedHandler = (url: string, opts?: RequestInit) => Response | null

/** Real `Response` object with a JSON body — no type assertions needed at call sites. */
export const okJson = (data: unknown): Response =>
  new Response(JSON.stringify(data), {
    status: 200,
    headers: { "content-type": "application/json" },
  })

export const errJson = (status: number, body: unknown = {}): Response =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  })

/**
 * Install a fetch mock. The generic preserves the input type so callers can
 * pass a vi.fn() mock and still reach its `.mock.calls` afterwards.
 */
export function installFetchMock<T extends FetchHandler>(handler: T): T {
  globalThis.fetch = handler
  return handler
}

/**
 * Find a button by its text content. Throws (instead of returning undefined)
 * so callers don't need non-null assertions.
 */
export function findButtonByText(
  wrapper: VueWrapper | DOMWrapper<Element>,
  text: string,
): DOMWrapper<Element> {
  const btn = wrapper.findAll("button").find((b) => b.text() === text)
  if (!btn) throw new Error(`Button with text "${text}" not found`)
  return btn
}

interface FetchMock {
  /** Match by url substring. */
  on(matcher: string, response: Response): void
  /** Custom predicate — return null to pass the request on to the next handler. */
  onMatching(predicate: RoutedHandler): void
  calls: () => unknown[][]
}

/**
 * URL-routed mock for `globalThis.fetch`. Handlers are checked in reverse
 * registration order, so calling `on('/x', ...)` after another `on('/x', ...)`
 * overrides the earlier response — useful for sequencing.
 */
export function makeFetchMock(): FetchMock {
  const handlers: RoutedHandler[] = []

  const mock = vi.fn(async (url: string, opts?: RequestInit): Promise<Response> => {
    for (const handler of [...handlers].reverse()) {
      const result = handler(url, opts)
      if (result !== null) return result
    }
    return okJson({})
  })

  installFetchMock(mock)

  return {
    on(matcher, response) {
      // Clone on each invocation — Response bodies are single-use streams
      handlers.push((url) => (url.includes(matcher) ? response.clone() : null))
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
