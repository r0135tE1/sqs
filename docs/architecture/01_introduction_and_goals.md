# Introduction and Goals

## Requirements Overview

"Fun with Flags" is a web-based application where you can test your knowledge about national flags. The game presents you with a country's flag and you have to guess the correct name. Correct guesses in a row increase your highscore.

## Quality Goals

| Priority | Quality Goal | Motivation |
| ---------- | ------------- | ------------ |
| 1 | **Testability & Verifiability** | The system must be testable across all levels (Unit, Integration, e2e, Load, and Penetration tests) |
| 1 | **Resilience** | The backend is dependent on an external API (`restcountries.com`). The application needs to handle downtime of external API and still be useable |
| 1 | **Deployability** | The system must be runnable without a complex setup process. Project setup and usage should be able with a minimal amount of steps |
| 1 | **Security** | The system must contain secured endpoints requiring authorization |

## Stakeholders

| Role/Name | Contact | Expectations |
| ----------- | --------- | -------------- |
| **Lecturer** | *felix.rampf@th-rosenheim.de* | Expects an project that adheres to the set software quality standards. The project has to be documented according to the arc42 standard with ADRs published on `readthedocs`. Expects a 15-minute presentation |
| **Students** | in lecture | Expect a presentation of the project, including a live demo. Will ask questions in a 5-minute Q&A session |
| **Development Team** | *robert.schlee@stud.th-rosenheim.de*, *albert.zichler@stud.th-rosenheim.de*, *marinus.graf@stud.th-rosenheim.de* | Needs clear architectural and interface definitions (Frontend/Backend/Persistence) to work in parallel and successfully create an web-app with enough test coverage |
