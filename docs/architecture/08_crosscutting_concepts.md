# Cross-cutting Concepts

## Authentication & Authorization

JWT (JSON Web Tokens) are used for stateless authentication. The backend issues a JWT upon successful login. The frontend stores the token and sends it as a Bearer token in the `Authorization` header for protected endpoints.

## Error Handling

The backend returns standardized HTTP status codes and JSON error responses:

| Scenario | HTTP Status |
|----------|-------------|
| Unauthenticated access to protected endpoint | 401 Unauthorized |
| Resource not found | 404 Not Found |
| API unreachable | 502 Bad Gateway |

## External API Integration

The backend is the sole point of communication with the public API. This keeps the external dependency encapsulated and allows for caching or fallback strategies in one place.

## Configuration Management

All sensitive configuration (DB credentials, JWT secret, API URLs) is stored in environment variables.

## Prefetch & Caching

On application startup the Backend fetches all flags from the public API and stores them inside the Persistence component. Additionally the Backend caches the fetched flags. The cache is refreshed periodically.

 If the external API is unreachable, the cached dataset serves as a fallback, ensuring the application remains functional even during third-party outages.

If the backend has no cached dataset and the external API is unreachable at the same time the Player is notified that the service is currently unavailable.

## Dependency Inversion

To decouple the system from external dependencies, the backend abstracts all calls to the public API behind an interface. Business logic depends on this abstraction rather than on the concrete HTTP client, making the integration point replaceable and independently testable.
