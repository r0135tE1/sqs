# Risks and Technical Debts

| Priority | Risk / Technical Debt | Description | Mitigation |
|----------|-----------------------|-------------|------------|
| 1 | **restcountries.com availability** | The application depends on a free, uncontrolled external API. If it goes down, no quiz questions can be served. | Cache country data on first fetch; serve cached data if API is unreachable |
| 2 | **JWT without revocation** | Issued JWTs remain valid until expiry. A stolen token cannot be invalidated. | Keep token lifetime short (e.g. 1 hour); implement a token blocklist if needed in the future |
| 3 | **No rate limiting (MVP)** | The API has no rate limiting, making it vulnerable to abuse or accidental overload. | Add rate limiting middleware (e.g. slowapi for FastAPI) post-MVP |
| 4 | **Streak stored in memory** | Active streak is not persisted mid-session. A backend restart loses the current streak. | Acceptable for MVP; consider session persistence if user experience requires it |
| 5 | **Single deployment environment** | MVP runs on a single server with no redundancy. | Acceptable for MVP scope; containerize with Docker for easier scaling later |
