from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials

from dependencies.auth import get_auth_service
from schemas import (
    LoginRequestSchema,
    LoginResponseSchema,
    RegisterRequestSchema,
    RefreshTokenResponseSchema
)
from dependencies.auth import security
from services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",    
    tags=["auth"],
)



@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequestSchema,
    service: AuthService = Depends(get_auth_service),
):
    return service.register(request)


@router.post(
    "/login",
    response_model=LoginResponseSchema,
)
def login(
    request: LoginRequestSchema,
    service: AuthService = Depends(get_auth_service),
):
    return service.login(request)


@router.post(
        "/refresh-token",
        response_model=RefreshTokenResponseSchema
)
def refresh_token(
    service: AuthService = Depends(get_auth_service),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    return service.refresh_access_token(credentials.credentials) 


@router.post("/logout")
def logout(
    service: AuthService = Depends(get_auth_service),
    credentials: HTTPAuthorizationCredentials = Depends(security)    
):
    
    return service.logout(credentials.credentials)

