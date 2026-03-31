# Introduction and Goals

## Requirements Overview

The project "Fun with Flags" is a web-based application where users can test their knowledge of national flags. The system presents a random flag, and the user must guess the corresponding country.

## Quality Goals

| Priority | Quality Goal | Motivation |
|----------|-------------|------------|
| 1 | **Testability & Verifiability** | The system must be testable across all levels (Unit, Integration, e2e, Load, and Penetration tests). |
| 1 | **Resilience** | The backend is dependent on the external API (`restcountries.com`). The application needs to handle downtime of external API and still be useable |
| 1 | **Deployability** | The system must be runnable without a complex setup process. Project setup and usage should be able with a minimal amount of steps. |
| 1 | **Security** | The system must contain secured endpoints requiring authorization |

## Stakeholders

| Role/Name | Contact | Expectations |
|-----------|---------|--------------|
| **Lecturer** | *felix.rampf@th-rosenheim.de* | Expects an project that adheres to the set software quality standards. The project has to be documented according to the arc42 standard with ADRs published on readthedocs. Expects a 15-minute presentation |
| **Students** | in lecture | Expect a presentation of the project, including a live demo of the software's core functionality. Will ask questions in a 5-minute Q&A session. |
| **Development Team** | *robert.schlee@stud.th-rosenheim.de*, *albert.zichler@stud.th-rosenheim.de*, *marinus.graf@stud.th-rosenheim.de* | Needs clear architectural and interface definitions (Frontend/Backend/Database) to work in parallel and successfully configure the runnable GitHub pipeline. |
