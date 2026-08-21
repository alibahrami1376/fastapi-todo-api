
# FastAPI Todo API 

A production-ready REST API for managing personal todo tasks, built with **FastAPI**, **SQLAlchemy**, **PostgreSQL**, and **JWT authentication** following a clean layered architecture.

- [Overview](#overview-en)
- [Features](#features-en)
- [Requirements](#requirements-en)
- [Configuration](#configuration-en)
- [Installation](#installation-en)
- [Usage](#usage-en)
  - [Seed fake data](#seed-en)
  - [Documentation](#documentation-en)
  - [Testing](#testing-en)
  - [Lint and Reformat](#lint-en)
- [Project Structure](#structure-en)
- [Architecture](#architecture-en)
- [Logging](#logging-en)
- [Planned Features](#Planned-Features)
- [License](#license-en)

---

<a name="overview-en"></a>
## Overview

FastAPI Todo API is a backend service that lets authenticated users create, read, update, delete and search their personal todo tasks.  
It is designed to demonstrate a real-world layered architecture with proper exception handling, JWT session management, and a full test suite.

---

<a name="features-en"></a>
## Features

- **JWT Authentication** — access token + refresh token with rotation
- **Refresh Token Fingerprint** — `SHA-256(IP + User-Agent)` embedded in the refresh JWT to prevent token theft across different clients
- **Session Management** — every login creates a session row; logout revokes both tokens
- **Todo CRUD** — create, list, get, partial update (PATCH), full replace (PUT), soft-delete
- **Todo Statistics** — `GET /api/v1/todos/stats` for total / completed / pending / overdue / by priority
- **Search / Filter / Sort / Paginate** — query by keyword, `is_completed`, `priority`, `due_from`, `due_to`; sort by any field; paginate with `page` + `page_size`
- **Soft Delete** — tasks are hidden, not physically removed
- **Custom Exception Hierarchy** — consistent JSON error shape across all errors
- **OpenAPI / Swagger** — every endpoint has `summary`, `description`, `response_model`, `status_code`, and examples
- **Database Indexes** — `owner_id` and composite `(owner_id, is_completed)` for fast queries
- **Alembic Migrations** — versioned schema evolution
- **Structured Logging** — Loguru + correlation ID (`X-Request-ID`), HTTP audit, and service-level events in NDJSON
- **Pytest Test Suite** — 32 tests with isolated test database and nested transactions

---

<a name="requirements-en"></a>
## Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| PostgreSQL | 13+ |
| [uv](https://docs.astral.sh/uv/) | latest |

Key dependencies (declared in `pyproject.toml`, locked in `uv.lock`):

- `fastapi` 0.141+
- `sqlalchemy` 2.0+
- `alembic` 1.18+
- `pydantic` 2.13+
- `pyjwt` 2.13+
- `passlib[bcrypt]`
- `psycopg2-binary`
- `python-dotenv`
- `loguru`, `asgi-correlation-id`
- Dev: `pytest`, `pytest-asyncio`, `ruff`, `pre-commit`, `faker`

---

<a name="configuration-en"></a>
## Configuration

Copy the sample and fill in your values:

```bash
cp app/.env.example app/.env
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | — | Main PostgreSQL connection string |
| `TEST_DATABASE_URL` | ✅ | — | Separate DB used only during pytest |
| `AUTH_JWT_SECRET_KEY` | ✅ | `change me` | Secret for signing JWTs — use a long random string in production |
| `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES` | | `10` | Access token lifetime |
| `AUTH_REFRESH_TOKEN_EXPIRE_DAYS` | | `30` | Refresh token lifetime |
| `TIMEZONE` | | `Asia/Tehran` | Used for `due_date` validation |
| `LOG_LEVEL` | | `INFO` | Loguru level (`DEBUG`, `INFO`, …) |
| `LOG_DIR` | | `logs` | Log directory (relative to `app/` unless absolute) |
| `LOG_ROTATION` | | `10 MB` | File rotation size/interval |
| `LOG_RETENTION` | | `14 days` | How long rotated files are kept |

**Example `app/.env`:**

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/todo
TEST_DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/todo_test

AUTH_JWT_SECRET_KEY=your-very-long-random-secret
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=10
AUTH_REFRESH_TOKEN_EXPIRE_DAYS=30

LOG_LEVEL=INFO
LOG_DIR=logs
LOG_ROTATION=10 MB
LOG_RETENTION=14 days
```

---

<a name="installation-en"></a>
## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/fastapi-todo-api.git
cd fastapi-todo-api

# 2. Install uv (if needed): https://docs.astral.sh/uv/getting-started/installation/

# 3. Install dependencies into .venv (runtime + dev)
uv sync

# 4. Set up environment variables
cp app/.env.example app/.env
# edit app/.env with your database credentials and secret key

# 5. Create databases in PostgreSQL
psql -U postgres -c "CREATE DATABASE todo;"
psql -U postgres -c "CREATE DATABASE todo_test;"

# 6. Run database migrations
cd app
TESTING=false uv run alembic upgrade head
cd ..

# 7. Start the development server
uv run uvicorn main:app --reload --app-dir app
```

The API will be available at `http://127.0.0.1:8000`.

Runtime-only install (no test/lint tools):

```bash
uv sync --no-dev
```

---

<a name="usage-en"></a>
## Usage

### Basic workflow

```
1. POST /api/v1/auth/register   – create an account
2. POST /api/v1/auth/login      – get access + refresh tokens
3. Use Authorization: Bearer <access_token> on all /todos and /users endpoints
4. POST /api/v1/auth/refresh    – rotate tokens (same User-Agent required)
5. POST /api/v1/auth/logout     – revoke session
```

### Todo endpoints

```
POST   /api/v1/todos            Create a task
GET    /api/v1/todos            List tasks (search/filter/sort/paginate)
GET    /api/v1/todos/stats      Aggregate statistics for the current user
GET    /api/v1/todos/{id}       Get a single task
PATCH  /api/v1/todos/{id}       Partial update
PUT    /api/v1/todos/{id}       Full replace
DELETE /api/v1/todos/{id}       Soft-delete
```

#### `GET /api/v1/todos/stats`

Returns counts for the authenticated user only (soft-deleted tasks are excluded).

| Field | Meaning |
|-------|---------|
| `total` | All active tasks |
| `completed` | `is_completed = true` |
| `pending` | `is_completed = false` |
| `overdue` | Pending tasks with `due_date` before today (app timezone) |
| `by_priority` | Counts for `low` / `medium` / `high` |

Example response:

```json
{
  "total": 10,
  "completed": 4,
  "pending": 6,
  "overdue": 2,
  "by_priority": {
    "low": 3,
    "medium": 5,
    "high": 2
  }
}
```

<a name="seed-en"></a>
### Seed fake data

```bash
cd app
uv run python scripts/seed.py
```

Generates fake users and tasks using `Faker`.

<a name="documentation-en"></a>
### Documentation

Interactive Swagger UI is available at:

```
http://127.0.0.1:8000/docs
```

ReDoc alternative:

```
http://127.0.0.1:8000/redoc
```

<a name="testing-en"></a>
### Testing

Make sure `TEST_DATABASE_URL` is set in `app/.env`, then:

```bash
# Apply migrations to the test database
cd app && TESTING=true uv run alembic upgrade head && cd ..

# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run only auth tests
uv run pytest tests/test_auth.py -v
```

All 32 tests run against an isolated test database using nested transactions — each test rolls back automatically.

<a name="lint-en"></a>
### Lint and Reformat

The project uses **Ruff** for linting and formatting:

```bash
# Check for lint errors
uv run ruff check app/

# Auto-fix
uv run ruff check app/ --fix

# Format code
uv run ruff format app/
```

---

<a name="structure-en"></a>
## Project Structure

```
fastapi-todo-api/
│
├── app/
│   ├── main.py                     FastAPI app entry point + exception handlers
│   ├── .env                        Environment variables (git-ignored)
│   ├── .env.example                Template for environment variables
│   │
│   ├── api/
│   │   ├── routers.py              Aggregates all versioned routers
│   │   └── v1/
│   │       ├── openapi_examples.py Centralized Swagger response examples
│   │       └── routes/
│   │           ├── auth.py         register / login / refresh / logout
│   │           ├── todos.py        CRUD + search/filter/sort/paginate
│   │           └── users.py        GET /me
│   │
│   ├── core/
│   │   ├── config.py               Pydantic settings (reads .env)
│   │   ├── database.py             SQLAlchemy engine + session + get_db
│   │   ├── exceptions.py           Custom exception classes + handlers
│   │   ├── security.py             JWT generate/decode + fingerprint hash
│   │   └── logging/                Loguru setup, filters, helpers
│   │
│   ├── middleware/
│   │   ├── correlation.py          Bridge X-Request-ID → Loguru context
│   │   └── logging.py              HTTP request/response audit
│   │
│   ├── dependencies/
│   │   ├── auth.py                 get_current_user, get_auth_service
│   │   └── task.py                 get_task_service
│   │
│   ├── messages/
│   │   ├── auth.py                 Auth-related string constants
│   │   └── task.py                 Task-related string constants
│   │
│   ├── migrations/
│   │   ├── env.py                  Alembic environment configuration
│   │   └── versions/               Migration files
│   │
│   ├── models/
│   │   ├── base.py                 BaseModel (id, timestamps, soft-delete)
│   │   ├── user.py                 UserModel
│   │   ├── task.py                 TaskModel (with indexes)
│   │   └── session.py              SessionModel
│   │
│   ├── repositories/
│   │   ├── user_repository.py      DB queries for users
│   │   ├── task_repository.py      DB queries for tasks (search/filter/sort)
│   │   └── session_repository.py  DB queries for sessions
│   │
│   ├── schemas/
│   │   ├── auth.py                 Request/response schemas for auth
│   │   ├── task.py                 Request/response/query schemas for tasks
│   │   └── user.py                 User response schema
│   │
│   ├── scripts/
│   │   └── seed.py                 Fake data generator
│   │
│   └── services/
│       ├── auth_service.py         Auth business logic
│       └── task_service.py         Task business logic
│
├── docs/
│   ├── flows.md                    All application flows documented
│   ├── flow-session.md             Session lifecycle diagram
│   └── logging-event-pattern.md    Logging flow & event structure
│
├── tests/
│   ├── conftest.py                 Test DB setup, fixtures, authenticated clients
│   ├── test_auth.py                Auth endpoint tests (17 tests)
│   └── test_todos.py               Todo endpoint tests (15 tests)
│
├── .python-version                 Pinned Python version for uv
├── pyproject.toml                  Project deps + Ruff/Pytest config
├── uv.lock                         Locked dependency versions
└── README.md
```

---

<a name="architecture-en"></a>
## Architecture

The project follows a **layered architecture**:

```
Request
  └─ Route (FastAPI)
       └─ Service (business logic)
            └─ Repository (data access)
                 └─ SQLAlchemy ORM
                      └─ PostgreSQL
```

| Layer | Responsibility |
|-------|----------------|
| **Routes** | HTTP handling, request validation, response serialization |
| **Services** | Business rules, orchestration, error decisions |
| **Repositories** | All DB queries — no business logic |
| **Models** | SQLAlchemy ORM table definitions |
| **Schemas** | Pydantic validation and serialization |

**Exception flow:**

All custom exceptions extend `BaseAppException` and are caught by `app_exception_handler`, which returns a consistent shape:

```json
{
  "success": false,
  "error": {
    "code": "TODO_NOT_FOUND",
    "message": "Todo not found"
  }
}
```

---

<a name="logging-en"></a>
## Logging

Structured logging with **Loguru** and **asgi-correlation-id**.

**Request flow:**

```text
CorrelationIdMiddleware
  → CorrelationIdLoggingMiddleware
    → Service logs (optional business steps)
      → RequestLoggingMiddleware (one HTTP audit per request)
```

| Piece | Role |
|-------|------|
| `X-Request-ID` / `correlation_id` | Joins all logs for one request |
| Service layer | Short business events (`event`, `operation`, ids) |
| Request logging middleware | One HTTP completed/failed audit (status, latency, masked headers on writes/errors) |
| `app/logs/app.jsonl` | NDJSON file sink with rotation/retention |
| stderr | Human-readable console (includes `cid=`) |

On unhandled 500s the app logs **once** at middleware level and returns a JSON 500 **without re-raising**, so Uvicorn does not duplicate the traceback. The response still carries `X-Request-ID`.

Details: [docs/logging-event-pattern.md](docs/logging-event-pattern.md).

---

<a name="Planned-Features"></a>
## Planned-Features
- [x] Add Fingerprint 
- [x] Structured logging
- [x] Centralized Logging — مخصوصاً خطاهای 500
- [x] Migrate to `uv` (pyproject.toml + uv.lock)
- [ ] Docker / Docker Compose  
- [ ] Redis  
- [ ] Rate Limiting
- [ ] Security Hardening
- [ ] CI/CD
- [ ] Deployment
- [ ] Health Check / Monitoring
- [ ] Documentation
- [ ] Bulk complete: `PATCH /api/v1/todos/bulk-complete`
- [ ] Bulk delete: `DELETE /api/v1/todos/bulk-delete`
- [x] Statistics: `GET /api/v1/todos/stats`
- [ ] create root: sen tasks by email(Celery) 
- [ ] create tak-weekly by  aspcheduler  (backup and  delet in database )
- [ ] chash in Redis برای session/auth lookup در get_current_user
- [ ] cash  rout state  after crate route 
- [ ] cash in todos realyy slow rout  

---

<a name="license-en"></a>
## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.