from core.security import (
    decode_access_token,
    decode_refresh_token,
    generate_access_token,
    generate_refresh_token,
    get_token_expiration_times,
)
from fastapi import HTTPException, status
from loguru import logger
from messages.auth import Messages
from repositories import SessionRepository, UserRepository
from schemas import LoginRequestSchema, RegisterRequestSchema


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        session_repo: SessionRepository,
    ):
        self.user_repo = user_repo
        self.session_repo = session_repo

    async def register(self, request: RegisterRequestSchema):
        existing_user = await self.user_repo.get_by_email(request.email)

        if existing_user:
            logger.bind(
                event="register_rejected",
                operation="auth.register",
                reason="user_already_exists",
            ).info("Register rejected")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Messages.user_already_exists,
            )

        user = await self.user_repo.create_user(
            email=request.email,
            password=request.password,
        )

        logger.bind(
            event="user_registered",
            operation="auth.register",
            user_id=user.id,
        ).info("User registered")

        return {
            "user_id": user.id,
            "email": user.email,
            "detail": Messages.registered_successfully,
        }

    async def login(
        self, request: LoginRequestSchema, fingerprint_hash: str | None = None
    ):
        user = await self.user_repo.get_by_email(request.email)

        if not user or not user.verify_password(request.password):
            logger.bind(
                event="login_failed",
                operation="auth.login",
                reason="invalid_credentials",
            ).info("Login failed")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Messages.invalid_credentials,
            )

        if not user.is_active or user.deleted_at is not None:
            logger.bind(
                event="login_failed",
                operation="auth.login",
                reason="inactive_or_deleted",
                user_id=user.id,
            ).info("Login failed")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Messages.invalid_credentials,
            )

        access_token, access_jti = generate_access_token(user.id)
        refresh_token, refresh_jti = generate_refresh_token(
            user.id, fingerprint_hash=fingerprint_hash
        )

        access_expires_at, refresh_expires_at = get_token_expiration_times()

        await self.session_repo.create(
            user_id=user.id,
            access_token_jti=access_jti,
            refresh_token_jti=refresh_jti,
            access_expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
        )

        logger.bind(
            event="user_logged_in",
            operation="auth.login",
            user_id=user.id,
        ).info("User logged in")

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_access_token(
        self, refresh_token: str, fingerprint_hash: str | None = None
    ):
        # fingerprint validation happens inside decode_refresh_token
        payload = decode_refresh_token(refresh_token, fingerprint_hash=fingerprint_hash)

        user_id = int(payload["sub"])
        refresh_jti = payload["jti"]

        session = await self.session_repo.get_by_refresh_token_jti(refresh_jti)

        if not session or session.refresh_revoked_at is not None:
            logger.bind(
                event="token_refresh_failed",
                operation="auth.refresh",
                reason="invalid_or_revoked_session",
                user_id=user_id,
            ).info("Token refresh failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=Messages.token_invalid,
            )

        user = await self.user_repo.get_by_id(user_id)

        if not user:
            logger.bind(
                event="token_refresh_failed",
                operation="auth.refresh",
                reason="user_not_found",
                user_id=user_id,
            ).info("Token refresh failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=Messages.user_not_found,
            )

        await self.session_repo.revoke_refresh_token(session)

        access_token, access_jti = generate_access_token(user.id)
        new_refresh_token, refresh_jti = generate_refresh_token(
            user.id, fingerprint_hash=fingerprint_hash
        )

        access_expires_at, refresh_expires_at = get_token_expiration_times()

        await self.session_repo.create(
            user_id=user.id,
            access_token_jti=access_jti,
            refresh_token_jti=refresh_jti,
            access_expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
        )

        logger.bind(
            event="token_refreshed",
            operation="auth.refresh",
            user_id=user.id,
        ).info("Token refreshed")

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    async def logout(self, access_token: str):
        payload = decode_access_token(access_token)

        access_jti = payload["jti"]

        session = await self.session_repo.get_by_access_token_jti(access_jti)

        if not session or session.access_revoked_at is not None:
            logger.bind(
                event="logout_failed",
                operation="auth.logout",
                reason="invalid_or_revoked_session",
            ).info("Logout failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=Messages.token_invalid,
            )

        await self.session_repo.revoke_access_token(session)
        await self.session_repo.revoke_refresh_token(session)

        logger.bind(
            event="user_logged_out",
            operation="auth.logout",
            user_id=session.user_id,
        ).info("User logged out")

        return {
            "detail": Messages.logged_out_successfully,
        }
