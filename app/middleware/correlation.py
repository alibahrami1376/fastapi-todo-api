from asgi_correlation_id import correlation_id
from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationIdLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = correlation_id.get()

        with logger.contextualize(
            correlation_id=request_id,
        ):
            return await call_next(request)
