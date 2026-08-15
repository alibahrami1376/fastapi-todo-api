from fastapi import APIRouter, Depends

from dependencies.auth import get_current_user
from models import UserModel
from schemas import UserResponseSchema


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/me",
    response_model=UserResponseSchema,
)
def get_me(
    current_user: UserModel = Depends(get_current_user),
):
    return current_user