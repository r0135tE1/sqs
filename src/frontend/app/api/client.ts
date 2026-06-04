import { API_URL } from "../config"

export class ApiError extends Error {
  constructor(public status: number, public detail: string) {
    super(detail)
    this.name = "ApiError"
  }
}

export class NetworkError extends Error {
  constructor(message = "Network connection failed") {
    super(message)
    this.name = "NetworkError"
  }
}

interface ApiFetchOptions extends Omit<RequestInit, "headers"> {
  token?: string | null
  headers?: Record<string, string>
  json?: unknown
}

/**
 * Single entry point for backend HTTP calls.
 * - JSON-encodes the body when `json` is provided
 * - Adds Authorization header when `token` is provided
 * - Throws NetworkError on connection failure
 * - Throws ApiError on non-2xx with the backend's `detail` if available
 * - Returns parsed JSON, or undefined for 204 No Content
 */
export async function apiFetch<T = unknown>(
  path: string,
  options: ApiFetchOptions = {}
): Promise<T> {
  const { token, headers = {}, json, body, ...rest } = options

  const finalHeaders: Record<string, string> = {
    Accept: "application/json",
    ...headers,
  }
  let finalBody = body
  if (json !== undefined) {
    finalHeaders["Content-Type"] = "application/json"
    finalBody = JSON.stringify(json)
  }
  if (token) {
    finalHeaders.Authorization = `Bearer ${token}`
  }

  let response: Response
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...rest,
      headers: finalHeaders,
      body: finalBody,
    })
  } catch {
    throw new NetworkError()
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const errBody = await response.json()
      if (typeof errBody?.detail === "string") detail = errBody.detail
    } catch {
      /* response was not JSON, keep default */
    }
    throw new ApiError(response.status, detail)
  }

  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}
