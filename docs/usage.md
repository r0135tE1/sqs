# Usage

This guide walks you through running the application locally with Docker.

## Running with Docker

Running the application with Docker is the recommended way to get started, as it
sets up the frontend, backend, and all required services for you.

### Prerequisites

Before you begin, make sure [Docker Desktop](https://www.docker.com/products/docker-desktop/)
is installed and running on your machine.

### Starting the application

First, generate the `.env` file. The setup script creates it for you and fills in
a randomly generated JWT secret:

```bash
./setup.sh
```

Next, build the images and start all containers:

```bash
docker compose up --build
```

The first build may take a few minutes.

### Available services

After startup, the following services are reachable:

| Service             | URL                          |
| ------------------- | ---------------------------- |
| Frontend            | <http://localhost>           |
| Backend API         | <http://localhost:8000>      |
| API Docs (Swagger)  | <http://localhost:8000/docs> |

### Stopping the application

To stop the running containers:

```bash
docker compose down
```

To additionally remove the database volumes (this deletes all stored data):

```bash
docker compose down -v
```

## Configuration

The application is configured through the `.env` file in the project root.
`./setup.sh` creates it from `.env.example` and fills in a randomly generated
`JWT_SECRET`. To change any setting, edit the `.env` file directly and restart
the containers.

### PostgreSQL

| Variable            | Default        | Description                                         |
| ------------------- | -------------- | --------------------------------------------------- |
| `POSTGRES_USER`     | `postgres`     | Database user created and used by the Postgres container |
| `POSTGRES_PASSWORD` | `postgres`     | Password for that user                              |
| `POSTGRES_DB`       | `funwithflags` | Name of the application database                    |

### JWT / Authentication

| Variable             | Default                          | Description                                          |
| -------------------- | -------------------------------- | ---------------------------------------------------- |
| `JWT_SECRET`         | *(random, set by `setup.sh`)*    | Secret key used to sign JWTs. Use a long random string in production |
| `JWT_ALGORITHM`      | `HS256`                          | Algorithm used to sign and verify tokens             |
| `JWT_EXPIRE_MINUTES` | `60`                             | Token validity in minutes                            |

### Other

| Variable            | Default                          | Description                                         |
| ------------------- | -------------------------------- | --------------------------------------------------- |
| `RESTCOUNTRIES_URL` | `https://restcountries.com/v3.1` | Base URL of the external country/flag API           |
| `LOG_LEVEL`         | `INFO`                           | Backend log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |


