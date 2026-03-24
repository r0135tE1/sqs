# Cross-cutting Concepts


<!-- This section describes crosscutting concepts (practices, patterns, regulations or solution ideas). Such concepts are often related to multiple building blocks. They may include many different topics, such as the topics shown in the following diagram:-->

## Authentication & Authorization
<!-- Calling services. need to authenticate themseves based upon remote procedure. Central authorization service has to be used --->

JWT (JSON Web Tokens) are used for stateless authentication. The backend issues a JWT upon successful login. The frontend stores the token and sends it as a Bearer token in the `Authorization` header for protected endpoints.

- Public endpoints (e.g. `GET /api/question`, `POST /api/guess`): no auth required
- Protected endpoints (e.g. `GET /api/highscore`, `POST /api/highscore`): JWT required

## Error Handling

The backend returns standardized HTTP status codes and JSON error responses:

| Scenario | HTTP Status |
|----------|-------------|
| Invalid guess input | 400 Bad Request |
| Unauthenticated access to protected endpoint | 401 Unauthorized |
| Resource not found | 404 Not Found |
| restcountries.com unreachable | 502 Bad Gateway |

## External API Integration

The backend is the sole point of communication with restcountries.com. The frontend never calls the external API directly. This keeps the external dependency encapsulated and allows for caching or fallback strategies in one place.

## Configuration Management

All sensitive configuration (DB credentials, JWT secret, API URLs) is stored in environment variables, never hardcoded. A `.env.example` file documents required variables without exposing values.

## Streak Logic

Streak state during an active session is managed in the backend. It is only persisted to the database when the user explicitly saves their highscore. This avoids unnecessary DB writes during gameplay.

## Caching

## Dependency Inversion