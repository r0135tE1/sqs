# Introduction and Goals

## Requirements Overview

The project "Spaß mit Flaggen" is a web-based application where users can test their knowledge of national flags. The system presents a random flag, and the user must guess the corresponding country.

<!--Guests can play via a publicly accessible endpoint, while registered users can save their highscore streak in a database via a secured endpoint, that requires a login. The required flag and country data is dynamically fetched from an external service, called `restcountries.com`. In addition to the core functionality, the system is developed to meet the various quality standards that good software should have. This includes a documented test concept covering the complete test pyramid, a runnable GitHub pipeline, and static code analysis.-->

## Quality Goals

| Priority | Quality Goal | Motivation |
|----------|-------------|------------|
| 1 | **Testability & Verifiability** | The system must be testable across all levels (Unit, Integration, e2e, Load, and Penetration tests). A static code analysis tool must verify that there are no open issues and that test coverage is at least 80%. |
| 1 | **Resilience** | The backend is dependent on the external API (`restcountries.com`). This connection must be protected using fail-safe architecture patterns to ensure our system remains stable even if the third-party provider experiences downtime. |
| 1 | **Deployability** | The system must be publicly accessible and runnable without a complex setup process. After checking out the code from the public GitHub repository, the entire project must be executable with a maximum of 2 commands (Docker Compose ). |
| 1 | **Security** | The system must have at least one secured endpoint. This endpoint shall only be accessible by authorized users|

## Stakeholders

| Role/Name | Contact | Expectations |
|-----------|---------|--------------|
| **Lecturer** | *felix.rampf@th-rosenheim.de* | Expects an project that adheres to the set software quality standards. The project has to be documented according to the arc42 standard with ADRs on readthedocs, and to be presented in a 15-minute talk |
| **Students** | in lecture | Expect a presentation of the project, including a live demo of the software's core functionality. Will ask questions in a 5-minute Q&A session. |
| **Development Team** | *robert.schlee@stud.th-rosenheim.de*, *albert.zichler@stud.th-rosenheim.de*, *marinus.graf@stud.th-rosenheim.de* | Needs clear architectural and interface definitions (Frontend/Backend/Database) to work in parallel and successfully configure the runnable GitHub pipeline. |