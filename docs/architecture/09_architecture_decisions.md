# Architecture Decisions

## ADR-001 Python Backend

**Status:** Accepted

**Context:** The course requires a backend service. Language choice was partly prescribed.

**Decision:** Use Python with FastAPI as the backend framework.

**Consequences:** FastAPI provides automatic OpenAPI documentation, async support, and built-in request validation via Pydantic — reducing boilerplate and making the API self-documenting.

---

## ADR-002 Vue 3 + TypeScript Frontend

**Status:** Accepted

**Context:** Frontend must be headless (data-driven only) and TypeScript was suggested.

**Decision:** Use Vue 3 with TypeScript as the frontend framework.

**Consequences:** Type safety reduces runtime errors. Vue 3's Composition API is well-suited for reactive quiz state management.

---

## ADR-003 JWT for Authentication

**Status:** Accepted

**Context:** The highscore endpoint must be secured. Session-based auth would require server-side session storage.

**Decision:** Use stateless JWT authentication.

**Consequences:** No server-side session state needed. JWTs can be validated without a DB lookup. Downside: tokens cannot be invalidated before expiry without a blocklist.

---

## ADR-004 Backend as sole consumer of restcountries.com

**Status:** Accepted

**Context:** The external API could be called directly from the frontend, but this would expose the external dependency to the client and prevent caching.

**Decision:** Only the backend calls restcountries.com. The frontend only communicates with the backend.

**Consequences:** External API changes only affect the backend. Enables response caching to reduce external calls and improve performance.

---

## ADR-005 PostgreSQL for Persistence

**Status:** Accepted

**Context:** User data and highscores are structured and relational by nature.

**Decision:** Use PostgreSQL as the persistence layer.

**Consequences:** Reliable ACID-compliant storage. Well-supported by Python ORMs (e.g. SQLAlchemy). Slight operational overhead compared to SQLite, but necessary for production-readiness.
