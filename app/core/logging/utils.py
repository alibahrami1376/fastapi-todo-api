import traceback

from fastapi import Request, Response

from core.logging.filters import mask_headers


def get_request_headers(request: Request) -> dict[str, str]:
    return mask_headers(request.headers)


def get_response_headers(response: Response) -> dict[str, str]:
    return mask_headers(response.headers)


def get_client_ip(request: Request) -> str | None:
    if request.client is None:
        return None

    return request.client.host


def get_exception_details(exc: Exception) -> dict:
    return {
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
        "traceback": traceback.format_exception(
            type(exc),
            exc,
            exc.__traceback__,
        ),
    }
