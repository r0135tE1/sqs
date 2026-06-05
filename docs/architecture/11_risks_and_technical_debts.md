# Risks and Technical Debts

## Overview

This section documents known risks and technical debts accepted during development.
Items are prioritized by their potential impact on system stability and security.

## Risks

| Priority | Risk | Description | Mitigation |
| ---------- | ------ | ------------- | ------------ |
| 1 | **API availability** | The application depends on a free, uncontrolled external API. If it goes down permanently, no new country data can be fetched. | Country data is prefetched and cached on startup. Cached data serves as fallback during outages. If no information is cached we provide an in-app message that our service is not avaible |
| 2 | **JWT without revocation** | Issued JWTs remain valid until expiry. A stolen token cannot be invalidated server-side. | Keep token lifetime short; implement a token blocklist if required in the future. |
| 3 | **No rate limiting** | The API has no rate limiting, making it vulnerable to abuse or accidental overload. Unauthenticated endpoints are particularly exposed. | Add rate limiting middleware |

## Technical Debts

| Priority | Technical Debt | Description | Mitigation |
| ---------- | --------------- | ------------- |------------ |
| 1 | **Active game session stored in memory only** | The current in-game score (streak) is tracked in the server-side `GameSessionStore` which is in-memory only. A backend restart loses all active sessions and their in-progress scores. Saved highscores in the database are not affected. | Acceptable for MVP; consider persistent session storage if user experience requires it. |
| 2 | **Single deployment environment** | The MVP runs on a single server with no redundancy or horizontal scaling | Acceptable for MVP scope; Docker Compose setup makes it straightforward to extend toward a multi-instance deployment later |
| 3 | **No structured logging** | The backend has no centralized logging or observability tooling. Debugging in production relies on container stdout. | Introduce structured logging and consider a log aggregation solution post-MVP |
