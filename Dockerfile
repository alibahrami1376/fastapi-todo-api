# syntax=docker/dockerfile:1

# Shared base: Python 3.10 + uv
FROM python:3.10-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /bin/

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first (better layer caching)
COPY pyproject.toml uv.lock .python-version ./


# -----------------------------------------------------------------------------
# Development — includes dev deps, reload, source bind-mount friendly
# -----------------------------------------------------------------------------
FROM base AS development

RUN uv sync --frozen --group dev

COPY app ./app
COPY scripts/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENV PYTHONPATH=/app/app \
    APP_ENV=development

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--app-dir", "app"]


# -----------------------------------------------------------------------------
# Production — runtime deps only, non-root, no reload
# -----------------------------------------------------------------------------
FROM base AS production

RUN uv sync --frozen --no-dev

COPY app ./app
COPY scripts/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh \
    && useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app

USER appuser

ENV PYTHONPATH=/app/app \
    APP_ENV=production

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "app", "--workers", "2"]
