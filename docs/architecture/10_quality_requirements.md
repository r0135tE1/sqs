# Quality Requirements

## Quality Requirements Overview

The most important quality goals are defined in [Section 1 – Introduction and Goals](01_introduction_and_goals.md). This section adds concrete scenarios to make them measurable.

## Quality Scenarios

| Quality Goal | Scenario | Priority |
|-------------|----------|----------|
| **Security** | An unauthenticated user calls `GET /api/highscore` → backend returns 401, no data is leaked | High |
| **Security** | A user submits a manipulated JWT → backend rejects the request with 401 | High |
| **Performance** | User requests a new quiz question → response arrives within 500ms under normal load | Medium |
| **Performance** | restcountries.com is temporarily slow → cached country data is served without delay | Medium |
| **Availability** | Backend process crashes and is restarted → application recovers without data loss | Medium |
| **Availability** | Public API is down -> application can provde cached calls from the API as questions | Medium |
| **Maintainability** | A developer adds a new endpoint → existing tests remain green, new endpoint follows existing API conventions | Low |
