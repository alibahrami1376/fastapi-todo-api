#!/bin/sh
set -e

# Optional: wait for Postgres when DATABASE_URL points at docker service "db"
if [ -n "${DATABASE_URL:-}" ]; then
  echo "Waiting for database..."
  # Simple retry loop using Python (always available in the image)
  python - <<'PY'
import os, sys, time
from urllib.parse import urlparse

url = os.environ.get("DATABASE_URL", "")
# postgresql+psycopg2://user:pass@host:port/db
parsed = urlparse(url.replace("postgresql+psycopg2", "postgresql", 1))
host = parsed.hostname or "db"
port = parsed.port or 5432

import socket
deadline = time.time() + 60
while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"Database is up at {host}:{port}")
            sys.exit(0)
    except OSError:
        time.sleep(1)
print(f"Timed out waiting for {host}:{port}", file=sys.stderr)
sys.exit(1)
PY
fi

# Optional: wait for Redis when REDIS_URL is set
if [ -n "${REDIS_URL:-}" ]; then
  echo "Waiting for Redis..."
  python - <<'PY'
import os, sys, time
from urllib.parse import urlparse

url = os.environ.get("REDIS_URL", "")
parsed = urlparse(url)
host = parsed.hostname or "redis"
port = parsed.port or 6379

import socket
deadline = time.time() + 60
while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"Redis is up at {host}:{port}")
            sys.exit(0)
    except OSError:
        time.sleep(1)
print(f"Timed out waiting for Redis at {host}:{port}", file=sys.stderr)
sys.exit(1)
PY
fi

# Run migrations unless explicitly skipped
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "Running alembic migrations..."
  cd /app/app
  TESTING=false uv run alembic upgrade head
  cd /app
fi

exec "$@"
