from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import settings
# from models.users import UserModel
# from repositories.user_repository import UserRepository
# from services.account_service import AccountService
# from schemas.accounts import (
#     RegisterRequestSchema,
#     LoginRequestSchema,
#     LoginResponseSchema,
# )
# from libs.auth.jwt_cookie_auth import get_authenticated_user
# from messages.accounts import Messages


router = APIRouter(
    prefix="/auth",    
    tags=["auth"],
)


# def get_account_service(db: Session = Depends(get_db)) -> AccountService:
#     user_repo = UserRepository(db)
#     return AccountService(user_repo)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register():
    return {}


@router.post("/login")
async def login():
    return {}


@router.post("/refresh-token")
async def refresh_token():
    return 


@router.post("/logout")
def logout():
    return {}


@router.get("/me")
async def session_verify():
   return {}