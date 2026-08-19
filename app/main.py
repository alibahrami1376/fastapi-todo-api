# route import
from api.routers import api_router
from core.exceptions import (
    BaseAppException,
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

app = FastAPI(
    title="Todo API",
    description=(
        "REST API for managing todos with JWT authentication, "
        "search/filter/sort/pagination, and layered architecture."
    ),
    version="1.0.0",
)


# # include route
app.include_router(api_router)

# add exeption
app.add_exception_handler(
    BaseAppException,
    app_exception_handler,
)

app.add_exception_handler(
    HTTPException,
    http_exception_handler,
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.add_exception_handler(
    Exception,
    unhandled_exception_handler,
)
