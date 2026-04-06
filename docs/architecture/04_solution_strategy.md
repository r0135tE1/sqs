# Solution Strategy

 "Fun With Flags" is designed to be easily deployable through containerization, with a clear separation between the application container and the API layer to ensure flexibility and scalability. To maintain robustness, the architecture incorporates mechanisms to remain resilient in the face of external API downtime, minimizing service disruption. In addition, a strong emphasis is placed on quality through comprehensive test coverage, following the principles of the test pyramid to balance unit, integration, and end-to-end testing effectively.

## Technology Decisions

- **Frontend:** TypeScript (Vue3) to provide a reactive single-page application
- **Backend:** Python to serve the REST API and orchestrate data flow
- **Persistence:** A relational database serves as the persistence layer
- **External API:** `restcountries.com` is used as the external service the backend must speak to
- **Infrastructure & CI/CD:** A runnable GitHub pipeline is used for continuous integration. The local deployment relies on Docker Compose to ensure the system starts with a maximum of 2 commands
- **Documentation & Modeling:** Documentation using the arc42 standard on readthedocs and a C4-model
- **Analysis:** Sonarcube to analyse test coverage
- **Testing:** Testing according to test pyramid

## Top-level Decomposition

The system is decomposed into 3 distinct layers:

1. **Frontend:** Handles user interaction and renders the UI. Calls Backend API
2. **Backend:** Contains the business logic, handles authentication, and acts as a gateway to the external service. It exposes at least one publicly accessible endpoint and at least one secured endpoint
3. **Persistence Layer:** Securely stores user credentials, highscores and flag information

## Decisions to Achieve Quality Goals

| Quality Goal | Approach |
| ------------- | ---------- |
| **Testability & Verifiability** | Documented test concept covering the entire test pyramid: <br> - unit test<br> - integration tests <br> - e2e tests <br> - penetration test <br> - load test <br> Static code analysis tool to guarantee 0 open issues and at least 80% test coverage in Sonarcube |
| **Resilience** | Prefetch all flags from the public API (`restcountries.com`) to provide a functional service even if the external API fails |
| **Deployability** | The source code is hosted in a public GitHub repository. By utilizing a runnable GitHub pipeline and containerization (Docker Compose), the checked-out code is fully runnable without further intervention using a maximum of 2 commands |
| **Security** | The endpoint for requesting highscores is secured in the backend and can only be successfully accessed by authorized users |
