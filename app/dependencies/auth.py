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

    session_repo = SessionRepository(db)
    user_repo = UserRepository(db)

    session = await session_repo.get_by_access_token_jti(access_jti)

    if not session or session.access_revoked_at is not None:
        raise AuthenticationException()

    user = await user_repo.get_by_id(user_id)

    if not user or not user.is_active:
        raise AuthenticationException()

    return user
