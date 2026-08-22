from core.config import settings
from core.logging.utils import get_client_ip
from core.rate_limit import check_rate_limit
from core.redis import get_redis
from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

# Stricter limits for credential / token endpoints (per IP).
_AUTH_LIMIT_PATHS = frozenset(
    {
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
    }
)

_SKIP_PREFIXES = (
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
)


def _rate_limit_response(
    *, retry_after: int, limit: int, remaining: int
) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please try again later.",
            },
        },
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
        },
    )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    IP-based fixed-window limits backed by Redis.

    - Global: all API routes
    - Auth: tighter window for login / register / refresh
    """

    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        path = request.url.path
        if any(path == p or path.startswith(p + "/") for p in _SKIP_PREFIXES):
            return await call_next(request)

        redis = get_redis()
        if redis is None:
            return await call_next(request)

        ip = get_client_ip(request) or "unknown"
        is_auth = path in _AUTH_LIMIT_PATHS and request.method == "POST"

        if is_auth:
            scope = "auth"
            limit = settings.RATE_LIMIT_AUTH_REQUESTS
            window = settings.RATE_LIMIT_AUTH_WINDOW_SECONDS
        else:
            scope = "global"
            limit = settings.RATE_LIMIT_GLOBAL_REQUESTS
            window = settings.RATE_LIMIT_GLOBAL_WINDOW_SECONDS

        key = f"rl:{scope}:{ip}"

        try:
            result = await check_rate_limit(
                redis,
                key=key,
                limit=limit,
                window_seconds=window,
            )
        except Exception:  # noqa: BLE001 — fail open if Redis errors mid-request
            logger.exception("Rate limit check failed; allowing request")
            return await call_next(request)

        if not result.allowed:
            logger.bind(
                event="rate_limit_exceeded",
                scope=scope,
                client_ip=ip,
                path=path,
                method=request.method,
                limit=result.limit,
            ).warning("Rate limit exceeded")
            return _rate_limit_response(
                retry_after=result.retry_after,
                limit=result.limit,
                remaining=result.remaining,
            )

        response = await call_next(request)
        response.headers.setdefault("X-RateLimit-Limit", str(result.limit))
        response.headers.setdefault(
            "X-RateLimit-Remaining",
            str(result.remaining),
        )
        return response
