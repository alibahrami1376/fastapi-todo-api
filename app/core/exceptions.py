from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from core.logging.utils import resolve_correlation_id


class BaseAppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code

        super().__init__(message)


class TodoNotFoundException(BaseAppException):
    def __init__(self):
        super().__init__(
            code="TODO_NOT_FOUND",
            message="Todo not found",
            status_code=404,
        )


class PermissionDeniedException(BaseAppException):
    def __init__(self):
        super().__init__(
            code="PERMISSION_DENIED",
            message="Permission denied",
            status_code=403,
        )


class InvalidSortFieldException(BaseAppException):
    def __init__(self):
        super().__init__(
            code="INVALID_SORT_FIELD",
            message="Invalid sort field",
            status_code=400,
        )


class AuthenticationException(BaseAppException):
    def __init__(self):
        super().__init__(
            code="AUTHENTICATION_ERROR",
            message="Authentication failed",
            status_code=401,
        )


class RateLimitExceededException(BaseAppException):
    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message="Too many requests. Please try again later.",
            status_code=429,
        )


def internal_error_response() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error",
            },
        },
    )


async def app_exception_handler(
    request: Request,
    exc: BaseAppException,
):
    headers = {}
    if isinstance(exc, RateLimitExceededException):
        headers["Retry-After"] = str(exc.retry_after)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        },
        headers=headers,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = jsonable_encoder(exc.errors())

    for error in errors:
        loc = error.get("loc", [])

        if "sort_by" in loc:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "error": {
                        "code": "INVALID_SORT_FIELD",
                        "message": "Invalid sort field",
                    },
                },
            )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": errors,
            },
        },
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    error_codes = {
        400: "BAD_REQUEST",
        401: "AUTHENTICATION_ERROR",
        403: "PERMISSION_DENIED",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
    }

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": error_codes.get(
                    exc.status_code,
                    "HTTP_ERROR",
                ),
                "message": str(exc.detail),
            },
        },
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    cid = resolve_correlation_id(request)

    if not getattr(request.state, "exception_logged", False):
        logger.bind(
            correlation_id=cid,
            event="unhandled_exception",
            method=request.method,
            path=request.url.path,
            status=500,
        ).exception("Unhandled exception")
        request.state.exception_logged = True

    return internal_error_response()


# ------------------------


class CustomValidationException(HTTPException):
    def __init__(
        self,
        detail: str = "Error in validating data",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(status_code=status_code, detail=detail)
