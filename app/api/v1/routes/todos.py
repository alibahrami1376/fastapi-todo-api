from api.v1.openapi_examples import (
    TASK_BULK_COMPLETE_RESPONSE_EXAMPLE,
    TASK_BULK_DELETE_RESPONSE_EXAMPLE,
    TASK_LIST_RESPONSE_EXAMPLE,
    TASK_RESPONSE_EXAMPLE,
    TASK_STATS_RESPONSE_EXAMPLE,
)
from dependencies.auth import get_current_user
from dependencies.task import get_task_service
from fastapi import APIRouter, Depends, status
from models import UserModel
from schemas import (
    TaskBulkCompleteResponseSchema,
    TaskBulkDeleteResponseSchema,
    TaskBulkIdsSchema,
    TaskCreateSchema,
    TaskListResponseSchema,
    TaskPutSchema,
    TaskQuerySchema,
    TaskResponseSchema,
    TaskStatsResponseSchema,
    TaskUpdateSchema,
)
from services.task_service import TaskService

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)


@router.post(
    "",
    summary="Create a new todo",
    description=(
        "Create a task for the authenticated user. "
        "Title is required (3–100 chars). due_date must be today or in the future."
    ),
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponseSchema,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Task created successfully",
            "content": {"application/json": {"example": TASK_RESPONSE_EXAMPLE}},
        },
    },
)
async def create_todo(
    request: TaskCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.create_task(
        user_id=current_user.id,
        task=request,
    )


@router.get(
    "",
    summary="List todos",
    description=(
        "Return a paginated list of the current user's tasks. "
        "Supports search (q), filters (is_completed, priority, due_from, due_to), "
        "and sorting (sort_by, order)."
    ),
    status_code=status.HTTP_200_OK,
    response_model=TaskListResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "description": "Paginated task list",
            "content": {"application/json": {"example": TASK_LIST_RESPONSE_EXAMPLE}},
        },
    },
)
async def get_todos(
    params: TaskQuerySchema = Depends(),
    current_user: UserModel = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.get_tasks(
        user_id=current_user.id,
        params=params,
    )


@router.get(
    "/stats",
    summary="Get todo statistics",
    description=(
        "Return aggregate statistics for the authenticated user's tasks: "
        "total, completed, pending, overdue, and counts by priority. "
        "Soft-deleted tasks are excluded. Overdue means pending with due_date before today."
    ),
    status_code=status.HTTP_200_OK,
    response_model=TaskStatsResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "description": "Task statistics",
            "content": {"application/json": {"example": TASK_STATS_RESPONSE_EXAMPLE}},
        },
    },
)
async def get_todo_stats(
    current_user: UserModel = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.get_stats(user_id=current_user.id)


@router.patch(
    "/bulk-complete",
    summary="Bulk-complete todos",
    description=(
        "Mark multiple tasks as completed for the authenticated user. "
        "All IDs must exist and belong to the current user; otherwise 404 or 403. "
        "Accepts 1–50 ids (duplicates are ignored)."
    ),
    status_code=status.HTTP_200_OK,
    response_model=TaskBulkCompleteResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "description": "Tasks marked as completed",
            "content": {
                "application/json": {"example": TASK_BULK_COMPLETE_RESPONSE_EXAMPLE}
            },
        },
    },
)
async def bulk_complete_todos(
    request: TaskBulkIdsSchema,
    current_user: UserModel = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.bulk_complete_tasks(
        user_id=current_user.id,
        task_ids=request.ids,
    )


@router.delete(
    "/bulk-delete",
    summary="Bulk soft-delete todos",
    description=(
        "Soft-delete multiple tasks owned by the authenticated user. "
        "All IDs must exist and belong to the current user; otherwise 404 or 403. "
        "Accepts 1–50 ids (duplicates are ignored)."
    ),
    status_code=status.HTTP_200_OK,
    response_model=TaskBulkDeleteResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "description": "Tasks soft-deleted",
            "content": {
                "application/json": {"example": TASK_BULK_DELETE_RESPONSE_EXAMPLE}
            },
        },
    },
)
async def bulk_delete_todos(
    request: TaskBulkIdsSchema,
    current_user: UserModel = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.bulk_delete_tasks(
        user_id=current_user.id,
        task_ids=request.ids,
    )


@router.get(
    "/{todo_id}",
    summary="Get a todo by ID",
    description=(
        "Return a single task owned by the authenticated user. "
        "Returns 404 if the task does not exist and 403 if it belongs to another user."
    ),
    status_code=status.HTTP_200_OK,
    response_model=TaskResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "description": "Task details",
            "content": {"application/json": {"example": TASK_RESPONSE_EXAMPLE}},
        },
    },
)
async def get_todo(
    todo_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.get_task(
        user_id=current_user.id,
        task_id=todo_id,
    )


@router.patch(
    "/{todo_id}",
    summary="Partially update a todo",
    description=(
        "Update only the fields provided in the request body. "
        "Omitted fields keep their current values."
    ),
    status_code=status.HTTP_200_OK,
    response_model=TaskResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "description": "Task updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        **TASK_RESPONSE_EXAMPLE,
                        "title": "Updated task title",
                        "is_completed": True,
                    }
                }
            },
        },
    },
)
async def update_patch_todo(
    todo_id: int,
    request: TaskUpdateSchema,
    current_user: UserModel = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.partial_update_task(
        user_id=current_user.id,
        task_id=todo_id,
        data=request,
    )


@router.put(
    "/{todo_id}",
    summary="Replace a todo",
    description=(
        "Replace all editable fields of a task. "
        "Every field in the body is required (full replacement)."
    ),
    status_code=status.HTTP_200_OK,
    response_model=TaskResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "description": "Task replaced successfully",
            "content": {
                "application/json": {
                    "example": {
                        **TASK_RESPONSE_EXAMPLE,
                        "is_completed": True,
                    }
                }
            },
        },
    },
)
async def update_put_todo(
    todo_id: int,
    request: TaskPutSchema,
    current_user: UserModel = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.update_task(
        user_id=current_user.id,
        task_id=todo_id,
        data=request,
    )


@router.delete(
    "/{todo_id}",
    summary="Delete a todo",
    description=(
        "Soft-delete a task owned by the authenticated user. "
        "The task is hidden from lists but not removed from the database."
    ),
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Task deleted successfully",
        },
    },
)
async def delete_todo(
    todo_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    await service.delete_task(
        user_id=current_user.id,
        task_id=todo_id,
    )
