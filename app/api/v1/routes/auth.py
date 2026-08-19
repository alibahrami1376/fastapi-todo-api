from dependencies.auth import get_auth_service, security
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from schemas import (
    LoginRequestSchema,
    LoginResponseSchema,
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
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponseSchema,
)
async def register(
    request: RegisterRequestSchema,
    service: AuthService = Depends(get_auth_service),
):
    return await service.register(request)


@router.post(
    "/login",
    response_model=LoginResponseSchema,
)
async def login(
    request: LoginRequestSchema,
    service: AuthService = Depends(get_auth_service),
):
    return await service.login(request)


@router.post("/refresh", response_model=RefreshTokenResponseSchema)
async def refresh_token(
    service: AuthService = Depends(get_auth_service),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return await service.refresh_access_token(credentials.credentials)


@router.post("/logout")
async def logout(
    service: AuthService = Depends(get_auth_service),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return await service.logout(credentials.credentials)
