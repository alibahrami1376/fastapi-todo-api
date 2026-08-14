from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import settings


router = APIRouter(
    prefix="/todos",    
    tags=["todos"],
)


# def get_account_service(db: Session = Depends(get_db)) -> AccountService:
#     user_repo = UserRepository(db)
#     return AccountService(user_repo)


@router.post("", status_code=status.HTTP_201_CREATED)
async def register():
    return {}


@router.get("")
async def get_todos():
    return {}


@router.get("/{todo_id}")
async def get_todo(todo_id: int):
    return {}


@router.patch("/{todo_id}")
def update_patch_todo(todo_id: int):
    return {}

@router.put("/{todo_id}")
def update_put_todo(todo_id: int):
    return {}


@router.delete("/{todo_id}")
def delete_todo(todo_id: int):
    return {}


