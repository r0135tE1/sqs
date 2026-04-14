# Architecture Constraints

## Technical Constraints

| Constraint | Background Background |
| ------------ | ------------------------ |
| **Programming Languages** | The possible languages consist of Typescript, Python, C# and Java |
| **Architecture** | The system must be divided into three layers: Frontend, Backend, and a Persistence layer |
| **Endpoints** | The API must expose at least one publicly accessible endpoint and at least one secured endpoint |
| **External Service Integration** | The backend must communicate with at least one publicly available endpoint |
| **Deployment & Execution** | The project must be runnable with a maximum of two commands after checkeout from the repository |
| **Documentation** | The documentation must be publicly available on `readthedocs` |

## Organizational Constraints

| Constraint | Background |
| ------------ | ------------------------ |
| **Version Control** | The project must be available in a public GitHub repository |
| **Examination Format** | The project must be presented in a 15-minute presentation, followed by a 5-minute Q&A session regarding the implementation. The presentation must include a live demo and a review of the static code analysis |
| **Team** | The project has to be developed by a team of three students |
| **Documentation** | Important architectural decisions must be recorded in Architecture Decision Records (ADRs) |
| **Use of AI-Tools** | AI assistants like ChatGPT and Copilot are allowed, but it is forbidden to generate the whole project using AI-Tools |

## Quality Constraints

| Constraint | Background |
| ------------ | ------------------------ |
| **Test Concept** | The software must have a documented and implemented test concept covering the entire test pyramid: <br> - Unit tests <br> - Integration tests <br> - End-to-end tests <br> - Penetration tests (e.g., integration test of the security logic) |
| **Test Coverage** | A tool for static code analysis must show no open issues and test coverage must be at least 80% |
| **CI/CD** | A runnable GitHub pipeline is required. |
