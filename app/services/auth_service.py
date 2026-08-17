from fastapi import HTTPException, status

from core.security import (
    decode_access_token,
    decode_refresh_token,
    generate_access_token,
    generate_refresh_token,
    get_token_expiration_times,
)
from messages.auth import Messages
from repositories import SessionRepository, UserRepository
from schemas import LoginRequestSchema, RegisterRequestSchema


class AuthService:

    async def __init__(
        self,
        user_repo: UserRepository,
        session_repo: SessionRepository,
    ):
        self.user_repo = user_repo
        self.session_repo = session_repo

    async def register(self, request: RegisterRequestSchema):
        existing_user = self.user_repo.get_by_email(request.email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Messages.user_already_exists,
            )

        self.user_repo.create_user(
            email=request.email,
            password=request.password,
        )

        return {
            "detail": Messages.registered_successfully,
        }

    async def login(self, request: LoginRequestSchema):
        user = self.user_repo.get_by_email(request.email)

        if not user or not user.verify_password(request.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Messages.invalid_credentials,
            )

        access_token, access_jti = generate_access_token(user.id)
        refresh_token, refresh_jti = generate_refresh_token(user.id)

        access_expires_at, refresh_expires_at = (
            get_token_expiration_times()
        )

        self.session_repo.create(
            user_id=user.id,
            access_token_jti=access_jti,
            refresh_token_jti=refresh_jti,
            access_expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
        )

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_access_token(self, refresh_token: str):
        payload = decode_refresh_token(refresh_token)

        user_id = int(payload["sub"])
        refresh_jti = payload["jti"]

        session = self.session_repo.get_by_refresh_token_jti(
            refresh_jti
        )

        if not session or session.refresh_revoked_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=Messages.token_invalid,
            )

        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=Messages.user_not_found,
            )

        # Revoke old refresh token
        self.session_repo.revoke_refresh_token(session)

        # Generate new token pair
        access_token, access_jti = generate_access_token(user.id)
        refresh_token, refresh_jti = generate_refresh_token(user.id)

        access_expires_at, refresh_expires_at = get_token_expiration_times()

        # Create new session
        self.session_repo.create(
            user_id=user.id,
            access_token_jti=access_jti,
            refresh_token_jti=refresh_jti,
            access_expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def logout(self, access_token: str):
        payload = decode_access_token(access_token)

        access_jti = payload["jti"]

        session = self.session_repo.get_by_access_token_jti(
            access_jti
        )

        if not session or session.access_revoked_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=Messages.token_invalid,
            )

        self.session_repo.revoke_access_token(session)
        self.session_repo.revoke_refresh_token(session)

        return {
            "detail": Messages.logged_out_successfully,
        }