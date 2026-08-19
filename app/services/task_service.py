from math import ceil

from core.exceptions import PermissionDeniedException, TodoNotFoundException
from fastapi import HTTPException, status
from messages import TaskMessages
from repositories import TaskRepository
from schemas import TaskCreateSchema, TaskQuerySchema, TaskUpdateSchema
from sqlalchemy.exc import SQLAlchemyError


class TaskService:
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    async def create_task(
        self,
        user_id: int,
        task: TaskCreateSchema,
    ):
        try:
            return await self.task_repo.create_task(
                title=task.title,
                description=task.description,
                priority=task.priority,
                due_date=task.due_date,
                owner_id=user_id,
            )

        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TaskMessages.TASK_CREATION_FAILED,
            )

    async def get_tasks(
        self,
        user_id: int,
        params: TaskQuerySchema,
    ):
        try:
            tasks, total = await self.task_repo.get_tasks(
                owner_id=user_id,
                params=params,
            )

            pages = ceil(total / params.page_size)

            return {
                "results": tasks,
                "page": params.page,
                "page_size": params.page_size,
                "total": total,
                "pages": pages,
            }

        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TaskMessages.TASK_FETCHING_FAILED,
            )

    async def get_task(
        self,
        user_id: int,
        task_id: int,
    ):
        try:
            task = await self.task_repo.get_by_id(task_id)

            if not task:
                raise TodoNotFoundException()

            if task.owner_id != user_id:
                raise PermissionDeniedException()

            return task

        except (
            TodoNotFoundException,
            PermissionDeniedException,
        ):
            raise

        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TaskMessages.TASK_FETCHING_FAILED,
            )

    async def update_task(
        self,
        user_id: int,
        task_id: int,
        data: TaskUpdateSchema,
    ):
        try:
            task = await self.task_repo.get_by_id_and_owner_id(
                task_id,
                user_id,
            )

            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=TaskMessages.TASK_NOT_FOUND,
                )

            task.title = data.title
            task.description = data.description
            task.priority = data.priority
            task.is_completed = data.is_completed
            task.due_date = data.due_date

            return await self.task_repo.update_task(task)

        except HTTPException:
            raise

        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TaskMessages.TASK_FETCHING_FAILED,
            )

    async def partial_update_task(
        self,
        user_id: int,
        task_id: int,
        data: TaskUpdateSchema,
    ):
        try:
            task = await self.task_repo.get_by_id_and_owner_id(
                task_id,
                user_id,
            )

            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=TaskMessages.TASK_NOT_FOUND,
                )

            update_data = data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(task, field, value)

            return await self.task_repo.update_task(task)

        except HTTPException:
            raise

        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TaskMessages.TASK_FETCHING_FAILED,
            )

    async def delete_task(
        self,
        user_id: int,
        task_id: int,
    ):

        try:
            task = await self.task_repo.get_by_id(task_id)

            if not task:
                raise TodoNotFoundException()

            if task.owner_id != user_id:
                raise PermissionDeniedException()

            await self.task_repo.delete_task(task)
        except (
            TodoNotFoundException,
            PermissionDeniedException,
        ):
            raise

        except HTTPException:
            raise

        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TaskMessages.TASK_FETCHING_FAILED,
            )
