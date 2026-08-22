# Command Reference — FastAPI Todo API

Quick copy-paste commands for local development, Docker, database, Redis, tests, and linting.

> Run all commands from the **repository root** unless noted otherwise.

---

## Setup & dependencies

```bash
# Install runtime + dev dependencies
uv sync

# Runtime only (no pytest/ruff)
uv sync --no-dev

# Copy environment template
cp app/.env.example app/.env
```

---

## Local development (without Docker)

Requires PostgreSQL and Redis running locally (`app/.env` configured).

```bash
# Create databases (once)
psql -U postgres -c "CREATE DATABASE todo;"
psql -U postgres -c "CREATE DATABASE todo_test;"

# Run migrations (main DB)
cd app && TESTING=false uv run alembic upgrade head && cd ..

# Start API with reload
uv run uvicorn main:app --reload --app-dir app
```

**URLs**

- API: http://127.0.0.1:8000  
- Swagger: http://127.0.0.1:8000/docs  
- ReDoc: http://127.0.0.1:8000/redoc  

```bash
# Seed fake data
cd app && uv run python scripts/seed.py && cd ..
```

---

## Database & migrations (Alembic)

```bash
# Upgrade main database
cd app && TESTING=false uv run alembic upgrade head && cd ..

# Upgrade test database (before pytest)
cd app && TESTING=true uv run alembic upgrade head && cd ..

# New migration (after model changes)
cd app && TESTING=false uv run alembic revision --autogenerate -m "describe change" && cd ..

# Show current revision
cd app && TESTING=false uv run alembic current && cd ..
```

---

## Docker Compose

Service names: `api` (dev), `api-prod` (prod profile), `db`, `redis`.  
Container names: `todo-api-dev`, `todo-api-prod`, `todo-db`, `todo-redis`.

### Start / stop

```bash
# Dev stack: Postgres + Redis + API (reload, ./app mounted)
docker compose up --build

# Detached
docker compose up -d --build

# Rebuild after dependency changes (pyproject.toml / Dockerfile)
docker compose up -d --build

# Stop containers (keep volumes)
docker compose down

# Stop and remove volumes (fresh DB/Redis data)
docker compose down -v
```

### Production profile

```bash
export AUTH_JWT_SECRET_KEY='your-long-random-secret'

docker compose --profile prod up -d --build db redis api-prod
```

### Logs & shell

```bash
# Follow API logs
docker compose logs -f api

# All services
docker compose logs -f

# Shell inside API container (use sh — no bash in slim image)
docker compose exec api sh

# Service status
docker compose ps
```

### Commands inside Docker

```bash
# Run tests in container
docker compose exec api uv run pytest
docker compose exec api uv run pytest -v
docker compose exec api uv run pytest tests/test_auth.py -v

# Run migrations manually
docker compose exec api sh -c "cd /app/app && TESTING=false uv run alembic upgrade head"

# One-off Python (cache/redis smoke test)
docker compose exec api uv run python -c "
import asyncio
from core.redis import init_redis, close_redis
from core.cache import cache_set, cache_get
async def main():
    await init_redis()
    await cache_set('test:hello', {'x': 1}, ttl_seconds=60)
    print(await cache_get('test:hello'))
    await close_redis()
asyncio.run(main())
"
```

---

## Redis

```bash
# Ping
docker compose exec redis redis-cli ping

# List all keys
docker compose exec redis redis-cli KEYS "*"

# Auth cache
docker compose exec redis redis-cli KEYS "auth:*"
docker compose exec redis redis-cli TTL "auth:session:<jti>"

# Todo stats cache
docker compose exec redis redis-cli GET "todos:stats:1"
docker compose exec redis redis-cli TTL "todos:stats:1"

# Rate limit keys
docker compose exec redis redis-cli KEYS "rl:*"

# Clear current DB (dev only — destructive)
docker compose exec redis redis-cli FLUSHDB
```

Local Redis (no Docker):

```bash
redis-cli -u redis://localhost:6379/0 ping
redis-cli -u redis://localhost:6379/0 KEYS "*"
```

---

## Testing

```bash
# Ensure test DB exists and is migrated
cd app && TESTING=true uv run alembic upgrade head && cd ..

# All tests (rate limit + cache disabled in conftest)
uv run pytest

# Verbose
uv run pytest -v

# Single file
uv run pytest tests/test_auth.py -v
uv run pytest tests/test_todos.py -v
```

---

## Lint & format (Ruff)

```bash
uv run ruff check app/

uv run ruff check app/ --fix

uv run ruff format app/
```

---

## API quick test (curl)

```bash
# Register
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Aa@123456","confirm_password":"Aa@123456"}'

# Login (save token)
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Aa@123456"}' | jq -r '.access_token')

# Current user
curl -s http://127.0.0.1:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN" | jq

# Todo stats
curl -s http://127.0.0.1:8000/api/v1/todos/stats \
  -H "Authorization: Bearer $TOKEN" | jq

# Logout
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## Git (common)

```bash
git status
git diff
git log --oneline -10

# New feature branch
git checkout -b feat/my-feature
```

---

## Troubleshooting

```bash
# Port already in use — stop stack
docker compose down

# API not picking up new Python package — rebuild
docker compose up -d --build

# Stale Redis keys after code changes
docker compose exec redis redis-cli FLUSHDB

# Check env inside API container
docker compose exec api printenv CACHE_ENABLED
docker compose exec api printenv REDIS_URL
docker compose exec api printenv RATE_LIMIT_ENABLED
```
