from api.v1.openapi_examples import USER_RESPONSE_EXAMPLE
from dependencies.auth import get_current_user
from fastapi import APIRouter, Depends, status
from models import UserModel
from schemas import UserResponseSchema

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/me",
    summary="Get current user profile",
    description=(
        "Return the profile of the authenticated user. "
        "Requires a valid access token in the Authorization header."
    ),
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "description": "Current user profile",
            "content": {"application/json": {"example": USER_RESPONSE_EXAMPLE}},
        },
    },
)
async def get_me(
    current_user: UserModel = Depends(get_current_user),
):
    return current_user
