import time

from core.exceptions import internal_error_response
from core.logging.utils import (
    get_client_ip,
    get_request_headers,
    get_response_headers,
    resolve_correlation_id,
)
from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        cid = resolve_correlation_id(request)

        try:
            response = await call_next(request)
        except Exception:  # noqa: BLE001 — convert any unhandled failure to one 500 log/response
            # BaseHTTPMiddleware often bypasses FastAPI exception handlers.
            # Log once here and return a 500 response so Uvicorn does not
            # log the same traceback again.
            response_time_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )
            if not getattr(request.state, "exception_logged", False):
                logger.bind(
                    correlation_id=cid,
                    event="http_request_failed",
                    method=request.method,
                    path=request.url.path,
                    query=str(request.url.query) or None,
                    status=500,
                    response_time_ms=response_time_ms,
                    client_ip=get_client_ip(request),
                    request_headers=get_request_headers(request),
                ).exception("HTTP request failed")
                request.state.exception_logged = True

            # Returning a response (not re-raising) lets CorrelationIdMiddleware
            # attach X-Request-ID and prevents Uvicorn duplicate tracebacks.
            return internal_error_response()

        response_time_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )
        bound = logger.bind(
            correlation_id=cid,
            event="http_request_completed",
            method=request.method,
            path=request.url.path,
            query=str(request.url.query) or None,
            status=response.status_code,
            response_time_ms=response_time_ms,
            client_ip=get_client_ip(request),
        )

        if response.status_code >= 400 or request.method in WRITE_METHODS:
            bound = bound.bind(
                request_headers=get_request_headers(request),
                response_headers=get_response_headers(response),
            )

        bound.info("HTTP request")
        return response
