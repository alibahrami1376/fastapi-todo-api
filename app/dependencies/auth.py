from core.cache import cache_get, cache_set
from core.cache_keys import auth_session_key, auth_user_key
from core.config import settings
from core.database import get_db
from core.exceptions import AuthenticationException
from core.security import decode_access_token
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models import UserModel
from repositories import SessionRepository, UserRepository
from services.auth_service import AuthService
from sqlalchemy.orm import Session

security = HTTPBearer(auto_error=False)


def _user_to_cache(user: UserModel) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_date": user.created_date.isoformat() if user.created_date else None,
        "updated_date": user.updated_date.isoformat() if user.updated_date else None,
        "deleted_at": user.deleted_at.isoformat() if user.deleted_at else None,
    }


def _user_from_cache(data: dict) -> UserModel | None:
    required = (
        "id",
        "email",
        "username",
        "is_active",
        "is_verified",
        "created_date",
        "updated_date",
    )
    if not all(k in data for k in required):
        return None

    from datetime import datetime

    user = UserModel(
        id=data["id"],
        email=data["email"],
        username=data["username"],
        is_active=data["is_active"],
        is_verified=data["is_verified"],
    )
    user.created_date = datetime.fromisoformat(data["created_date"])
    user.updated_date = datetime.fromisoformat(data["updated_date"])
    if data.get("deleted_at"):
        user.deleted_at = datetime.fromisoformat(data["deleted_at"])
    return user


def get_auth_service(
    db: Session = Depends(get_db),
) -> AuthService:
    user_repo = UserRepository(db)
    session_repo = SessionRepository(db)

    return AuthService(
        user_repo=user_repo,
        session_repo=session_repo,
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> UserModel:

    if credentials is None:
        raise AuthenticationException()

    token = credentials.credentials
    payload = decode_access_token(token)

    access_jti = payload["jti"]
    user_id = int(payload["sub"])

    session_key = auth_session_key(access_jti)
    user_key = auth_user_key(user_id)

    # --- session از cache ---
    cached_session = await cache_get(session_key)
    if cached_session is not None:
        if cached_session.get("revoked"):
            raise AuthenticationException()
        if cached_session.get("user_id") != user_id:
            raise AuthenticationException()
    else:
        session_repo = SessionRepository(db)
        session = await session_repo.get_by_access_token_jti(access_jti)

        if not session or session.access_revoked_at is not None:
            raise AuthenticationException()

        await cache_set(
            session_key,
            {"user_id": session.user_id, "revoked": False},
            ttl_seconds=settings.CACHE_AUTH_TTL_SECONDS,
        )

    # --- user از cache ---
    cached_user = await cache_get(user_key)
    user = _user_from_cache(cached_user) if cached_user is not None else None

    if user is None:
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)

        if not user or not user.is_active or user.deleted_at is not None:
            raise AuthenticationException()

        await cache_set(
            user_key,
            _user_to_cache(user),
            ttl_seconds=settings.CACHE_AUTH_TTL_SECONDS,
        )

    if not user.is_active or user.deleted_at is not None:
        raise AuthenticationException()

    return user
