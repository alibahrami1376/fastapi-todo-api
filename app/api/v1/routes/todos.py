from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from dependencies.auth import get_current_user
from models import UserModel
from repositories import TaskRepository
from schemas import (
    TaskCreateSchema,
    TaskListResponseSchema,
    TaskPutSchema,
    TaskQuerySchema,
    TaskResponseSchema,
    TaskUpdateSchema,
)
from services.task_service import TaskService
from dependencies.task import get_task_service

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)



@router.post(
    "",
    response_model=TaskResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_todo(
    request: TaskCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return service.create_task(
        user_id=current_user.id,
        task=request,
    )


@router.get(
    "",
    response_model=TaskListResponseSchema,
)
def get_todos(
    params: TaskQuerySchema = Depends(),
    current_user: UserModel = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return service.get_tasks(
        user_id=current_user.id,
        params=params,
    )


@router.get(
    "/{todo_id}",
    response_model=TaskResponseSchema,
)
def get_todo(
    todo_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return service.get_task(
        user_id=current_user.id,
        task_id=todo_id,
    )


@router.patch(
    "/{todo_id}",
    response_model=TaskResponseSchema,
)
def update_patch_todo(
    todo_id: int,
    request: TaskUpdateSchema,
    current_user: UserModel = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return service.partial_update_task(
        user_id=current_user.id,
        task_id=todo_id,
        data=request,
    )


@router.put(
    "/{todo_id}",
    response_model=TaskResponseSchema,
)
def update_put_todo(
    todo_id: int,
    request: TaskPutSchema,
    current_user: UserModel = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return service.update_task(
        user_id=current_user.id,
        task_id=todo_id,
        data=request,
    )


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_todo(
    todo_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    service.delete_task(
        user_id=current_user.id,
        task_id=todo_id,
    )