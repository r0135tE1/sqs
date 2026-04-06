# Quality Requirements

## Quality Requirements Overview

The most important quality goals are defined in [Section 1 – Introduction and Goals](01_introduction_and_goals.md).

### Nice-to-Have

| Quality Goal | Scenario | Priority |
| ------------- | ---------- | ---------- |
| **Maintainability** | A developer adds a new endpoint → existing tests still pass, new endpoint follows existing API conventions | Medium |
| **Maintainability** | The external API is replaced by a different provider → only the concrete HTTP client implementation needs to change, business logic is unaffected | Medium |
| **Performance** | User requests a new quiz question → response arrives within 500ms under normal load | Medium |
| **Performance** | API is temporarily slow → cached country data is served without added latency | Medium |
| **Configurability** | A developer changes DB credentials or the JWT secret → no code change is required, only environment variables needs to be updated | Low |
| **Usability** | The external API is unavailable during a session → the user receives a clear in-app message instead of an error screen | Low |
