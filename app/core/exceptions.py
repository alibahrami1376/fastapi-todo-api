from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from http import HTTPStatus


# === Custom Exception Classes ===
class PermissionDenied(HTTPException):
    def __init__(self, detail: str = "Permission Denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class AuthenticationFailed(HTTPException):
    def __init__(self, detail: str = "Authentication Failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class NotAuthenticated(HTTPException):
    def __init__(self, detail: str = "Not Authenticated"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class CustomValidationException(HTTPException):
    def __init__(self, detail: str = "Error in validating data",status_code:int=status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


# === Exception Handlers ===
async def custom_validation_exception_handler(request: Request, exc: CustomValidationException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "status_code": exc.status_code,
                "message": HTTPStatus(exc.status_code).description,
                "detail": exc.detail
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "status_code": 422,
                "message": HTTPStatus(422).description,
                "detail": exc.errors()
            }
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "status_code": exc.status_code,
                "message": HTTPStatus(exc.status_code).description,
                "detail": exc.detail
            }
        }
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "status_code": 500,
                "message": "Internal Server Error",
                "detail": str(exc)
            }
        }
    )