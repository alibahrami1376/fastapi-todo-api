# shell داخل API
docker compose exec api sh

# pytest
docker compose exec api uv run pytest

# لاگ
docker compose logs -f api


docker compose up -d
docker compose logs api



docker compose exec redis redis-cli ping
# PONG
docker compose exec redis redis-cli KEYS "*"