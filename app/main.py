from api.routers import api_router
from asgi_correlation_id import CorrelationIdMiddleware
from core.exceptions import (
    BaseAppException,
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from core.logging.config import setup_logging
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from middleware.correlation import CorrelationIdLoggingMiddleware
from middleware.logging import RequestLoggingMiddleware

# =========================
# Logging
# =========================

setup_logging()


# =========================
# FastAPI
# =========================

app = FastAPI(
    title="Todo API",
    description=(
        "REST API for managing todos with JWT authentication, "
        "search/filter/sort/pagination, and layered architecture."
    ),
    version="1.0.0",
)


# =========================
# Middleware
# =========================
app.add_middleware(CorrelationIdLoggingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(CorrelationIdMiddleware)


# =========================
# Routes
# =========================

app.include_router(api_router)


# =========================
# Exception handlers
# =========================

app.add_exception_handler(
    BaseAppException,
    app_exception_handler,
)

app.add_exception_handler(
    HTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    unhandled_exception_handler,
)
