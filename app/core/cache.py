"""Redis cache-aside helpers (JSON values)."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger

from core.config import settings
from core.redis import get_redis


def _enabled() -> bool:
    return settings.CACHE_ENABLED and get_redis() is not None


async def cache_get(key: str) -> Any | None:
    if not _enabled():
        return None

    redis = get_redis()
    try:
        raw = await redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception:  # noqa: BLE001
        logger.exception("Cache get failed for key={}", key)
        return None


async def cache_set(key: str, value: Any, ttl_seconds: int) -> None:
    if not _enabled():
        return

    redis = get_redis()
    try:
        await redis.set(key, json.dumps(value, default=str), ex=ttl_seconds)
    except Exception:  # noqa: BLE001
        logger.exception("Cache set failed for key={}", key)


async def cache_delete(key: str) -> None:
    if not _enabled():
        return

    redis = get_redis()
    try:
        await redis.delete(key)
    except Exception:  # noqa: BLE001
        logger.exception("Cache delete failed for key={}", key)


async def cache_delete_pattern(pattern: str) -> None:
    """Delete keys matching pattern, e.g. todos:list:42:*"""
    if not _enabled():
        return

    redis = get_redis()
    try:
        keys = [key async for key in redis.scan_iter(match=pattern)]
        if keys:
            await redis.delete(*keys)
    except Exception:  # noqa: BLE001
        logger.exception("Cache delete_pattern failed for pattern={}", pattern)
