from collections.abc import Mapping

SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "proxy-authorization",
}


def mask_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {
        key: "***" if key.lower() in SENSITIVE_HEADERS else value
        for key, value in headers.items()
    }
