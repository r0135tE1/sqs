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

The backend is the sole point of communication with restcountries.com. The frontend never calls the external API directly. This keeps the external dependency encapsulated and allows for caching or fallback strategies in one place.

## Configuration Management

All sensitive configuration (DB credentials, JWT secret, API URLs) is stored in environment variables, never hardcoded into the project files.

## Prefetch & Caching

The backend caches responses from restcountries.com to improve resilience. If the external API is unreachable, the cached dataset serves as a fallback, ensuring the application remains functional even during third-party outages. The cache is populated on first request and refreshed periodically.

If the backend has no cached dataset or if all flags from the cached dataset have been called the application automatically saves the streak for the next game and notify the user that the service is currently unavailable.

## Dependency Inversion

To decouple the system from external dependencies, the backend abstracts all calls to the public API behind an interface. Business logic depends on this abstraction rather than on the concrete HTTP client, making the integration point replaceable and independently testable.
