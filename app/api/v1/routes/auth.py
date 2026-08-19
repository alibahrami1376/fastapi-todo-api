from api.v1.openapi_examples import (
    LOGIN_RESPONSE_EXAMPLE,
    LOGOUT_RESPONSE_EXAMPLE,
    REFRESH_RESPONSE_EXAMPLE,
    REGISTER_RESPONSE_EXAMPLE,
)
from dependencies.auth import get_auth_service, security
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from schemas import (
    LoginRequestSchema,
    LoginResponseSchema,
    LogoutResponseSchema,
    RefreshTokenResponseSchema,
    RegisterRequestSchema,
    RegisterResponseSchema,
)
from services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    summary="Register a new user",
    description=(
        "Create a new account with email and password. "
        "Password must meet complexity rules (uppercase, lowercase, digit, special char)."
    ),
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponseSchema,
    responses={
        status.HTTP_201_CREATED: {
            "description": "User registered successfully",
            "content": {"application/json": {"example": REGISTER_RESPONSE_EXAMPLE}},
        },
    },
)
async def register(
    request: RegisterRequestSchema,
    service: AuthService = Depends(get_auth_service),
):
    return await service.register(request)


@router.post(
    "/login",
    summary="Login",
    description=(
        "Authenticate with email and password. "
        "Returns a short-lived access token and a long-lived refresh token."
    ),
    status_code=status.HTTP_200_OK,
    response_model=LoginResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "description": "Login successful",
            "content": {"application/json": {"example": LOGIN_RESPONSE_EXAMPLE}},
        },
    },
)
async def login(
    request: LoginRequestSchema,
    service: AuthService = Depends(get_auth_service),
):
    return await service.login(request)


@router.post(
    "/refresh",
    summary="Refresh access token",
    description=(
        "Exchange a valid refresh token (sent as Bearer) for a new access/refresh token pair. "
        "The previous refresh token is revoked."
    ),
    status_code=status.HTTP_200_OK,
    response_model=RefreshTokenResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "description": "Tokens refreshed successfully",
            "content": {"application/json": {"example": REFRESH_RESPONSE_EXAMPLE}},
        },
    },
)
async def refresh_token(
    service: AuthService = Depends(get_auth_service),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return await service.refresh_access_token(credentials.credentials)


@router.post(
    "/logout",
    summary="Logout",
    description=(
        "Revoke the current session. Send the access token as Bearer. "
        "Both access and refresh tokens for this session become invalid."
    ),
    status_code=status.HTTP_200_OK,
    response_model=LogoutResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "description": "Logged out successfully",
            "content": {"application/json": {"example": LOGOUT_RESPONSE_EXAMPLE}},
        },
    },
)
async def logout(
    service: AuthService = Depends(get_auth_service),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return await service.logout(credentials.credentials)
