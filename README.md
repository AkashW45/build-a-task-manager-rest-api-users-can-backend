# Task Manager API

A production-ready REST API for task management built with FastAPI, PostgreSQL, and SQLAlchemy.

## Features

- Create, list, update, and delete tasks
- Automatic OpenAPI documentation at `/docs`
- Asynchronous database operations
- UUID-based task identifiers
- Alembic migrations for database schema management

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL (via asyncpg)
- **ORM**: SQLAlchemy (async)
- **Migrations**: Alembic
- **Containerization**: Docker & Docker Compose

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (optional, for containerized deployment)

## Local Development

### 1. Clone the repository

```bash
git clone <repo-url>
cd task-api-service
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy `.env.example` to `.env` and adjust values as needed.

### 5. Start a local PostgreSQL instance

Using Docker:

```bash
docker run -d --name task-db -e POSTGRES_USER=taskuser -e POSTGRES_PASSWORD=taskpass -e POSTGRES_DB=tasks -p 5432:5432 postgres:16
```

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start the API server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## Docker Compose (Production-like setup)

```bash
docker compose up --build
```

This will start both the API server and the PostgreSQL database. The API will be available at `http://localhost:8000`.

## API Endpoints

| Method | Endpoint       | Description          |
|--------|----------------|----------------------|
| POST   | `/tasks`       | Create a new task    |
| GET    | `/tasks`       | List all tasks       |
| GET    | `/tasks/{id}`  | Retrieve a task      |
| PUT    | `/tasks/{id}`  | Update a task        |
| DELETE | `/tasks/{id}`  | Delete a task        |

## License

MIT