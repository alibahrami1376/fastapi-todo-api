import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from jwt.exceptions import DecodeError, InvalidSignatureError

from core.config import settings
from core.exceptions import AuthenticationException


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


def generate_refresh_token(user_id: int) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())

    payload = {
        "type": "refresh",
        "sub": str(user_id),
        "jti": jti,
        "iat": now,
        "exp": now + timedelta(days=settings.AUTH_REFRESH_TOKEN_EXPIRE_DAYS),
    }

    token = jwt.encode(
        payload,
        settings.AUTH_JWT_SECRET_KEY,
        algorithm="HS256",
    )

    return token, jti


def decode_access_token(token: str) -> dict:
    try:
        decoded = jwt.decode(
            token,
            settings.AUTH_JWT_SECRET_KEY,
            algorithms=["HS256"],
        )

        if decoded.get("type") != "access":
            raise AuthenticationException()

        if not decoded.get("sub"):
            raise AuthenticationException()

        if not decoded.get("jti"):
            raise AuthenticationException()

        return decoded

    except AuthenticationException:
        raise

    except InvalidSignatureError:
        raise AuthenticationException()

    except DecodeError:
        raise AuthenticationException()


def decode_refresh_token(token: str) -> dict:
    try:
        decoded = jwt.decode(
            token,
            settings.AUTH_JWT_SECRET_KEY,
            algorithms=["HS256"],
        )

        if decoded.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, token type not valid",
            )

        if not decoded.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, sub not in the payload",
            )

        if not decoded.get("jti"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, jti not in the payload",
            )

        return decoded

    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, invalid signature",
        )

    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, decode failed",
        )


def get_token_expiration_times() -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)

    access_expires_at = now + timedelta(
        minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_expires_at = now + timedelta(days=settings.AUTH_REFRESH_TOKEN_EXPIRE_DAYS)

    return access_expires_at, refresh_expires_at
