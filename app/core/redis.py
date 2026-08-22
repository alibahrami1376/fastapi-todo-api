from loguru import logger
from redis.asyncio import Redis

from core.config import settings

_redis: Redis | None = None


async def init_redis() -> None:
    """Connect to Redis on app startup. Rate limiting is skipped if unavailable."""

    global _redis

    if not settings.RATE_LIMIT_ENABLED and not settings.CACHE_ENABLED:
        logger.info("Redis not needed (rate limit + cache disabled)")
        return

    client = Redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )

    try:
        await client.ping()
    except Exception:  # noqa: BLE001
        logger.exception(
            "Redis unavailable at {}; rate limiting will be skipped",
            settings.REDIS_URL,
        )
        await client.aclose()
        _redis = None
        return

    _redis = client
    logger.info("Redis connected ({})", settings.REDIS_URL)


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
        logger.info("Redis connection closed")


def get_redis() -> Redis | None:
    return _redis
