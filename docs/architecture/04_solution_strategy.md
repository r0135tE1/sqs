# Solution Strategy

The core strategy for "Fun with Flags" is to build a robust, easily deployable web application that strictly adheres to the set software quality standards. Automation for testing, code analysis, and deployment is used to achieve the quality goals.

## Technology Decisions

* **Frontend:** TypeScript (Vue3) to provide a reactive single-page application.
* **Backend:** Python to serve the REST API and orchestrate data flow.
* **Persistence:** A relational database (PostgreSQL) serves as the persistence layer.
* **External API:** `restcountries.com` is used as the external service the backend must speak to.
* **Infrastructure & CI/CD:** A runnable GitHub pipeline is used for continuous integration. The local deployment relies on Docker Compose to ensure the system starts with a maximum of 2 commands.
* **Documentation & Modeling:** Documentation using the arc42 standard on readthedocs and a C4-model.
* **Analysis:** Sonarcube to analyse test coverage.

## Top-level Decomposition

The system is decomposed into 3 distinct layers:
1. **Frontend:** Handles user interaction and renders the UI.
2. **Backend:** Contains the business logic, handles authentication, and acts as a gateway to the external service. It exposes at least one publicly accessible endpoint for guest users and at least one secured endpoint (login context) for registered users.
3. **Persistence Layer:** Securely stores user credentials and highscores.

## Decisions to Achieve Quality Goals

| Quality Goal | Approach |
|-------------|----------|
| **Testability & Verifiability** | Documented test concept covering the entire test pyramid: Unit, Integration, e2e, Penetration (testing the secured endpoints), and Load tests. Static code analysis tool to guarantee 0 open issues and at least 80% test coverage in Sonarcube. |
| **Resilience** | To prevent the backend from crashing when the external `restcountries.com` API fails, a fail-safe mechanism needs to be implemented.|
| **Deployability** | The source code is hosted in a public GitHub repository. By utilizing a runnable GitHub pipeline and containerization (Docker Compose), the checked-out code is fully runnable without further intervention using a maximum of 2 commands with a Docker compose. |
| **Security** | The endpoint for requesting the highscores is secured in the backend and can only be successfully accessed by logged-in users |

## Organizational Decisions

* **Tooling:**  AI assistants like ChatGPT and Copilot are permitted tools, but it is ensured that the generated code and documentation is fully understood.
