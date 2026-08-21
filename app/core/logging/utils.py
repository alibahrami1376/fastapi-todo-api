from asgi_correlation_id import correlation_id
from fastapi import Request, Response

from core.logging.filters import mask_headers

REQUEST_ID_HEADER = "X-Request-ID"


def get_request_headers(request: Request) -> dict[str, str]:
    return mask_headers(request.headers)


def get_response_headers(response: Response) -> dict[str, str]:
    return mask_headers(response.headers)


def get_client_ip(request: Request) -> str | None:
    if request.client is None:
        return None

    return request.client.host


def resolve_correlation_id(request: Request | None = None) -> str:
    """
    Return the request correlation id.

    ``CorrelationIdMiddleware`` sets a ContextVar, but ``BaseHTTPMiddleware``
    can drop contextvars across its internal task boundary. Fall back to the
    request header that CorrelationIdMiddleware writes onto the scope.
    """
    cid = correlation_id.get()
    if not cid and request is not None:
        cid = request.headers.get(REQUEST_ID_HEADER)

    if cid:
        # Restore ContextVar inside BaseHTTPMiddleware so later logs / send
        # callbacks can see it again.
        correlation_id.set(cid)
        return cid

    return "-"


def set_request_id_header(response: Response, cid: str) -> None:
    if cid and cid != "-":
        response.headers.setdefault(REQUEST_ID_HEADER, cid)
