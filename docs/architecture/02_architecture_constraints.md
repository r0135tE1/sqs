# Architecture Constraints

## Technical Constraints

| Constraint | Background / Motivation |
| ------------ | ------------------------ |
| **Programming Languages** | The possible languages consist of Typescript, Python, C# and Java. For this project typeScript was chosen for the frontend and python for the backend|
| **Architecture** | The system must be divided into three layers: Frontend, Backend, and a Persistence layer. |
| **Endpoint Security** | The API must expose at least one publicly accessible endpoint and at least one secured endpoint. |
| **External Service Integration** | The backend must communicate with at least one publicly available endpoint |
| **Deployment & Execution** | The project must be runnable with a maximum of two commands after checkeout from the repository |
| **Documentation** | The documentation must be publicly available on `readthedocs` |

## Organizational Constraints

| Constraint | Background |
| ------------ | ------------------------ |
| **Version Control** | The project must be available in a public GitHub repository |
| **CI/CD** | A runnable GitHub pipeline is required. |
| **Examination Format** | The project must be presented in a 15-minute presentation, followed by a 5-minute Q&A session regarding the implementation. The presentation must include a live demo and a review of the static code analysis |
| **Team** | The project has to be developed by a team of three students |
| **Documentation Standard** | Important architectural decisions must be recorded in Architecture Decision Records (ADRs) |
