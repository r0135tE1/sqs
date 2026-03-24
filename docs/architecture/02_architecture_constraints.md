# Architecture Constraints

## Technical Constraints

| Constraint | Background / Motivation |
|------------|------------------------|
| **Programming Languages** | TypeScript was chosen for the frontend and Python for the backend|
| **3-Tier Architecture** | The system must be divided into at least three layers: Frontend, Backend, and a Persistence layer (database holding user information and highscores). |
| **Endpoint Security** | The API must expose at least one publicly accessible endpoint and at least one secured endpoint (login). |
| **External Service Integration** | The backend must communicate with at least one external service (`restcountries.com`).  |
| **Deployment & Execution** | The project must be publicly accessible and runnable with a maximum of 2 commands after checking it out (docker compose).

## Organizational Constraints

| Constraint | Background / Motivation |
|------------|------------------------|
| **Version Control & CI/CD** | The source code must be hosted in a public GitHub repository. Furthermore, a runnable GitHub pipeline is strictly required. |
| **Examination Format** | The project must be presented in a 15-minute presentation, followed by a 5-minute Q&A session regarding the implementation. This presentation must include a live demo and a review of the static code analysis. |
| **Team** | The project has to be developed by a team of 3 students|

## Conventions

| Convention | Background / Motivation |
|------------|------------------------|
| **Documentation Standard** | The architecture must be documented following the arc42 standard. Important architectural decisions must be recorded in Architecture Decision Records (ADRs). The documentation must be well-structured and publicly available on `readthedocs`. The documentation is written in english |
| **Quality Assurance & Testing** | The software must feature a documented and implemented test concept covering the complete test pyramid (Unit, Integration, e2e, Penetration for secured endpoints, and Load tests). |
| **Static Code Analysis** | A static code analysis tool must be used, demonstrating 0 open issues and a minimum test coverage of 80%. |
| **Architecture Modeling** | To provide an overview of the project structure and main components, a C4-model must be used. |
| **Usage of AI Tools** | Tools like ChatGPT or Copilot are permitted, but the team must understand the generated code completely, as this will be evaluated. |