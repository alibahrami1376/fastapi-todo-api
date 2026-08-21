from core.logging.utils import resolve_correlation_id
from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationIdLoggingMiddleware(BaseHTTPMiddleware):
    """
    Bridge asgi-correlation-id → Loguru.

    Must sit *inside* ``CorrelationIdMiddleware`` and *outside*
    ``RequestLoggingMiddleware`` so Loguru context is active while HTTP
    logging runs (including the exception path).
    """

    async def dispatch(self, request: Request, call_next):
        request_id = resolve_correlation_id(request)

        with logger.contextualize(correlation_id=request_id):
            return await call_next(request)
