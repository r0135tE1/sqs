# Architecture Decisions

## ADR-001 Python Backend

**Status:** Accepted

**Context:** The course requires a backend service. Language choice was partly prescribed.

**Decision:** Use Python with FastAPI as the backend framework.

**Consequences:** FastAPI provides automatic OpenAPI documentation, async support, and built-in request validation via Pydantic — reducing boilerplate and making the API self-documenting.

## ADR-002 Vue 3 + TypeScript Frontend

**Status:** Accepted

**Context:** Frontend must be headless (data-driven only) and TypeScript was suggested.

**Decision:** Use Vue 3 with TypeScript as the frontend framework.

**Consequences:** Type safety reduces runtime errors. Vue 3's Composition API is well-suited for reactive quiz state management.

## ADR-003 JWT for Authentication

**Status:** Accepted

**Context:** The highscore endpoint must be secured. Session-based auth would require server-side session storage.

**Decision:** Use stateless JWT authentication. Public endpoints (e.g. question delivery, guess submission) require no authentication.

**Consequences:** No server-side session state needed. JWTs can be validated without a DB lookup. Downside: tokens cannot be invalidated before expiry without a blocklist.


## ADR-004 Backend as Sole Consumer of API

**Status:** Accepted

**Context:** The external API could be called directly from the frontend, but this would expose the external dependency to the client and prevent caching or fallback handling.

**Decision:** Only the backend calls the public API. The frontend only communicates with the backend. All external API access is encapsulated behind a backend interface following the dependency inversion principle.

**Consequences:** External API changes only affect the backend. Enables response caching to reduce external calls and improve resilience. If the external API becomes unavailable, fallback and degradation logic is handled in one place.


## ADR-005 PostgreSQL for Persistence

**Status:** Accepted

**Context:** User data and highscores are structured and relational by nature.

**Decision:** Use PostgreSQL as the persistence layer.

**Consequences:** Reliable ACID-compliant storage. Well-supported by Python ORMs (e.g. SQLAlchemy).

## ADR-006 Prefetch and Cache of Country Dataset

**Status:** Accepted

**Context:** The application depends on `restcountries.com` for country and flag data. Repeated live requests increase latency and create a single point of failure. The dataset is largely static and suitable for caching.

**Decision:** The backend prefetches the full country dataset from restcountries.com at startup, loads it into an in-memory cache (`FlagCache`), and persists it to the `flags` database table. On a subsequent restart, if the API is unreachable, the backend falls back to the persisted data to populate the cache.

**Consequences:** Improved resilience and response times during gameplay. The application remains functional across restarts even during extended API outages.
