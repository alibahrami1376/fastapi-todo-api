"""Redis fixed-window rate limiter."""

from __future__ import annotations

from dataclasses import dataclass

from redis.asyncio import Redis

# Atomic INCR + EXPIRE on first hit (window seconds in ARGV[1]).
_INCR_WITH_EXPIRE = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
local ttl = redis.call('TTL', KEYS[1])
return {current, ttl}
"""


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after: int


async def check_rate_limit(
    redis: Redis,
    *,
    key: str,
    limit: int,
    window_seconds: int,
) -> RateLimitResult:
    current, ttl = await redis.eval(
        _INCR_WITH_EXPIRE,
        1,
        key,
        window_seconds,
    )
    current = int(current)
    ttl = int(ttl)
    retry_after = ttl if ttl > 0 else window_seconds
    remaining = max(0, limit - current)
    return RateLimitResult(
        allowed=current <= limit,
        limit=limit,
        remaining=remaining,
        retry_after=retry_after,
    )
