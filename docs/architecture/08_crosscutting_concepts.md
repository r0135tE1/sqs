# Cross-cutting Concepts

## Authentication & Authorization

JWT (JSON Web Tokens) are used for stateless authentication. The backend issues a JWT upon successful login. The frontend stores the token and sends it as a Bearer token in the `Authorization` header for protected endpoints.

## Error Handling

The backend returns standardized HTTP status codes and JSON error responses:

| Scenario | HTTP Status |
|----------|-------------|
| Invalid answer submission (unknown `question_id`) | 400 Bad Request |
| Unauthenticated access to protected endpoint / invalid login credentials | 401 Unauthorized |
| Resource not found (session, user, highscore, or no unseen flags left) | 404 Not Found |
| Username already taken on registration | 409 Conflict |
| Request body fails validation (e.g. blank/weak password) | 422 Unprocessable Entity |

Note: when the external API was unreachable at startup, the flag cache stays empty and `GET /game/flag` returns `404 Not Found` (no flag available) rather than a gateway error — see *Prefetch & Caching* below.

## External API Integration

The backend is the sole point of communication with the public API. This keeps the external dependency encapsulated and allows for caching or fallback strategies in one place.

## Configuration Management

All sensitive configuration (DB credentials, JWT secret, API URLs) is stored in environment variables.

## Prefetch & Caching

On application startup the backend fetches all country metadata and flag SVG images from the public API, loads them into the in-memory `FlagCache`, and persists them to the `flags` database table. The cache is loaded once at startup and serves all flag requests for the lifetime of the process. There is no periodic refresh of flag data. A separate background task removes expired game sessions every hour, but does not reload flags.

If the external API is unreachable at startup, the backend falls back to the flag data previously persisted in the database and loads it into the in-memory cache. If both the API and the database are empty (e.g. on first boot with no connectivity), the cache stays empty and the backend degrades gracefully — no crash occurs, but the player is notified that the service is currently unavailable.

## Dependency Inversion

To decouple the system from external dependencies, the backend abstracts all calls to the public API behind an interface. Business logic depends on this abstraction rather than on the concrete HTTP client, making the integration point replaceable and independently testable.
