import hashlib
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidSignatureError

from core.config import settings
from core.exceptions import AuthenticationException


def build_fingerprint_hash(ip: str, user_agent: str) -> str:
    """Return a SHA-256 hex digest of the client IP and User-Agent string."""
    raw = f"{ip}:{user_agent}"
    return hashlib.sha256(raw.encode()).hexdigest()


def generate_access_token(user_id: int) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())

    payload = {
        "type": "access",
        "sub": str(user_id),
        "jti": jti,
        "iat": now,
        "exp": now + timedelta(minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    token = jwt.encode(
        payload,
        settings.AUTH_JWT_SECRET_KEY,
        algorithm="HS256",
    )

    return token, jti


def generate_refresh_token(
    user_id: int,
    fingerprint_hash: str | None = None,
) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())

    payload = {
        "type": "refresh",
        "sub": str(user_id),
        "jti": jti,
        "iat": now,
        "exp": now + timedelta(days=settings.AUTH_REFRESH_TOKEN_EXPIRE_DAYS),
    }

    if fingerprint_hash is not None:
        payload["fph"] = fingerprint_hash

    token = jwt.encode(
        payload,
        settings.AUTH_JWT_SECRET_KEY,
        algorithm="HS256",
    )

    return token, jti


def _decode_token(token: str, expected_type: str) -> dict:
    """Decode and validate a JWT, raising AuthenticationException on any failure."""
    try:
        decoded = jwt.decode(
            token,
            settings.AUTH_JWT_SECRET_KEY,
            algorithms=["HS256"],
        )

        if decoded.get("type") != expected_type:
            raise AuthenticationException()

        if not decoded.get("sub"):
            raise AuthenticationException()

        if not decoded.get("jti"):
            raise AuthenticationException()

        return decoded

    except AuthenticationException:
        raise

    except (ExpiredSignatureError, InvalidSignatureError, DecodeError):
        raise AuthenticationException()


def decode_access_token(token: str) -> dict:
    return _decode_token(token, "access")


def decode_refresh_token(token: str, fingerprint_hash: str | None = None) -> dict:
    """Decode a refresh token and optionally validate the embedded fingerprint."""
    decoded = _decode_token(token, "refresh")

    token_fph = decoded.get("fph")
    if token_fph is not None and fingerprint_hash != token_fph:
        raise AuthenticationException()

    return decoded


def get_token_expiration_times() -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)

    access_expires_at = now + timedelta(
        minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_expires_at = now + timedelta(days=settings.AUTH_REFRESH_TOKEN_EXPIRE_DAYS)

    return access_expires_at, refresh_expires_at
