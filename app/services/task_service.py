from math import ceil

from core.exceptions import PermissionDeniedException, TodoNotFoundException
from fastapi import HTTPException, status
from loguru import logger
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
            created = await self.task_repo.create_task(
                title=task.title,
                description=task.description,
                priority=task.priority,
                due_date=task.due_date,
                owner_id=user_id,
            )
            logger.bind(
                event="task_created",
                operation="tasks.create",
                task_id=created.id,
                user_id=user_id,
            ).info("Task created")
            return created

        except SQLAlchemyError:
            logger.bind(
                event="task_create_failed",
                operation="tasks.create",
                user_id=user_id,
            ).exception("Task create failed")
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

    async def get_stats(self, user_id: int):
        try:
            stats = await self.task_repo.get_stats(owner_id=user_id)
            logger.bind(
                event="tasks_stats_fetched",
                operation="tasks.stats",
                user_id=user_id,
                total=stats["total"],
                completed=stats["completed"],
                pending=stats["pending"],
                overdue=stats["overdue"],
            ).info("Task stats fetched")
            return stats

        except SQLAlchemyError:
            logger.bind(
                event="tasks_stats_failed",
                operation="tasks.stats",
                user_id=user_id,
            ).exception("Task stats fetch failed")
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
            task = await self.task_repo.get_by_id(task_id)

            if not task:
                raise TodoNotFoundException()

            if task.owner_id != user_id:
                raise PermissionDeniedException()

            task.title = data.title
            task.description = data.description
            task.priority = data.priority
            task.is_completed = data.is_completed
            task.due_date = data.due_date

            updated = await self.task_repo.update_task(task)
            logger.bind(
                event="task_updated",
                operation="tasks.update",
                task_id=task_id,
                user_id=user_id,
            ).info("Task updated")
            return updated

        except (
            TodoNotFoundException,
            PermissionDeniedException,
        ):
            raise

        except HTTPException:
            raise

        except SQLAlchemyError:
            logger.bind(
                event="task_update_failed",
                operation="tasks.update",
                task_id=task_id,
                user_id=user_id,
            ).exception("Task update failed")
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
            task = await self.task_repo.get_by_id(task_id)

            if not task:
                raise TodoNotFoundException()

            if task.owner_id != user_id:
                raise PermissionDeniedException()

            update_data = data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(task, field, value)

            updated = await self.task_repo.update_task(task)
            logger.bind(
                event="task_updated",
                operation="tasks.partial_update",
                task_id=task_id,
                user_id=user_id,
                fields=list(update_data.keys()),
            ).info("Task updated")
            return updated

        except (
            TodoNotFoundException,
            PermissionDeniedException,
        ):
            raise

        except HTTPException:
            raise

        except SQLAlchemyError:
            logger.bind(
                event="task_update_failed",
                operation="tasks.partial_update",
                task_id=task_id,
                user_id=user_id,
            ).exception("Task update failed")
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
            logger.bind(
                event="task_deleted",
                operation="tasks.delete",
                task_id=task_id,
                user_id=user_id,
            ).info("Task deleted")
        except (
            TodoNotFoundException,
            PermissionDeniedException,
        ):
            raise

        except HTTPException:
            raise

        except SQLAlchemyError:
            logger.bind(
                event="task_delete_failed",
                operation="tasks.delete",
                task_id=task_id,
                user_id=user_id,
            ).exception("Task delete failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TaskMessages.TASK_FETCHING_FAILED,
            )

    async def _resolve_owned_tasks(
        self,
        user_id: int,
        task_ids: list[int],
    ) -> list:
        tasks = []
        for task_id in task_ids:
            task = await self.task_repo.get_by_id(task_id)

            if not task:
                raise TodoNotFoundException()

            if task.owner_id != user_id:
                raise PermissionDeniedException()

            tasks.append(task)

        return tasks

    async def bulk_complete_tasks(
        self,
        user_id: int,
        task_ids: list[int],
    ):
        try:
            tasks = await self._resolve_owned_tasks(user_id, task_ids)
            await self.task_repo.bulk_complete(tasks)
            updated_ids = [task.id for task in tasks]

            logger.bind(
                event="tasks_bulk_completed",
                operation="tasks.bulk_complete",
                user_id=user_id,
                updated=len(updated_ids),
                ids=updated_ids,
            ).info("Tasks bulk completed")

            return {
                "updated": len(updated_ids),
                "ids": updated_ids,
            }

        except (
            TodoNotFoundException,
            PermissionDeniedException,
        ):
            raise

        except SQLAlchemyError:
            logger.bind(
                event="tasks_bulk_complete_failed",
                operation="tasks.bulk_complete",
                user_id=user_id,
                ids=task_ids,
            ).exception("Tasks bulk complete failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TaskMessages.TASK_BULK_UPDATE_FAILED,
            )

    async def bulk_delete_tasks(
        self,
        user_id: int,
        task_ids: list[int],
    ):
        try:
            tasks = await self._resolve_owned_tasks(user_id, task_ids)
            deleted_ids = [task.id for task in tasks]
            await self.task_repo.bulk_soft_delete(tasks)

            logger.bind(
                event="tasks_bulk_deleted",
                operation="tasks.bulk_delete",
                user_id=user_id,
                deleted=len(deleted_ids),
                ids=deleted_ids,
            ).info("Tasks bulk deleted")

            return {
                "deleted": len(deleted_ids),
                "ids": deleted_ids,
            }

        except (
            TodoNotFoundException,
            PermissionDeniedException,
        ):
            raise

        except SQLAlchemyError:
            logger.bind(
                event="tasks_bulk_delete_failed",
                operation="tasks.bulk_delete",
                user_id=user_id,
                ids=task_ids,
            ).exception("Tasks bulk delete failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TaskMessages.TASK_BULK_DELETION_FAILED,
            )
