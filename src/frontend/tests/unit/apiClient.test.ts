import { describe, it, expect, vi, beforeEach } from "vitest"
import { apiFetch, ApiError, NetworkError } from "../../app/api/client"

describe("apiFetch", () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it("returns parsed JSON on success", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ hello: "world" }),
    }) as typeof fetch

    const data = await apiFetch<{ hello: string }>("/test")
    expect(data).toEqual({ hello: "world" })
  })

  it("returns undefined on 204 No Content", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 204,
      json: async () => { throw new Error("no body") },
    }) as typeof fetch

    const data = await apiFetch("/test")
    expect(data).toBeUndefined()
  })

  it("attaches Authorization header when token is provided", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({}),
    })
    globalThis.fetch = fetchMock as typeof fetch

    await apiFetch("/test", { token: "my-jwt" })
    const init = vi.mocked(globalThis.fetch).mock.calls[0]?.[1]
    const headers = init?.headers as Record<string, string>
    expect(headers.Authorization).toBe("Bearer my-jwt")
  })

  it("encodes json body and sets Content-Type", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({}),
    })
    globalThis.fetch = fetchMock as typeof fetch

    await apiFetch("/test", { method: "POST", json: { a: 1 } })
    const init = vi.mocked(globalThis.fetch).mock.calls[0]?.[1]
    expect(init?.body).toBe(JSON.stringify({ a: 1 }))
    expect((init?.headers as Record<string, string>)["Content-Type"]).toBe("application/json")
  })

  it("throws NetworkError when fetch itself rejects", async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error("ECONNREFUSED")) as typeof fetch

    await expect(apiFetch("/test")).rejects.toBeInstanceOf(NetworkError)
  })

  it("throws ApiError with backend detail on non-2xx", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 409,
      json: async () => ({ detail: "Username already taken" }),
    }) as typeof fetch

    try {
      await apiFetch("/test")
      expect.fail("should have thrown")
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError)
      expect((err as ApiError).status).toBe(409)
      expect((err as ApiError).detail).toBe("Username already taken")
    }
  })

  it("throws ApiError with default detail when body is not JSON", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => { throw new Error("not json") },
    }) as typeof fetch

    try {
      await apiFetch("/test")
      expect.fail("should have thrown")
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError)
      expect((err as ApiError).status).toBe(500)
      expect((err as ApiError).detail).toContain("500")
    }
  })
})
