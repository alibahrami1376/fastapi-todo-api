import time

from asgi_correlation_id import correlation_id
from core.logging.utils import (
    get_client_ip,
    get_exception_details,
    get_request_headers,
    get_response_headers,
)
from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        try:
            response = await call_next(request)

        except Exception as exc:
            response_time = time.perf_counter() - start_time

            logger.exception(
                "HTTP request failed",
                method=request.method,
                path=request.url.path,
                status=500,
                response_time=f"{response_time:.3f}s",
                correlation_id=correlation_id.get(),
                client_ip=get_client_ip(request),
                request_headers=get_request_headers(request),
                **get_exception_details(exc),
            )

            raise

        response_time = time.perf_counter() - start_time

        logger.info(
            "HTTP request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            response_time=f"{response_time:.3f}s",
            correlation_id=correlation_id.get(),
            client_ip=get_client_ip(request),
            request_headers=get_request_headers(request),
            response_headers=get_response_headers(response),
        )

        return response
