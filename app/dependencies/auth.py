from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import decode_access_token
from models import UserModel
from repositories import SessionRepository, UserRepository
from services.auth_service import AuthService


security = HTTPBearer()


def get_auth_service(
    db: Session = Depends(get_db),
) -> AuthService:
    user_repo = UserRepository(db)
    session_repo = SessionRepository(db)

    return AuthService(
        user_repo=user_repo,
        session_repo=session_repo,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> UserModel:
    token = credentials.credentials

    payload = decode_access_token(token)

    access_jti = payload["jti"]
    user_id = int(payload["sub"])

    session_repo = SessionRepository(db)
    user_repo = UserRepository(db)

    session = session_repo.get_by_access_token_jti(access_jti)

    if not session or session.access_revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked access token.",
        )

    user = user_repo.get_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active or does not exist.",
        )

    return user