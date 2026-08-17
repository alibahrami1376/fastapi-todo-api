from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Query, Session

from models import PriorityTypes, TaskModel
from schemas import (
    SortOrder,
    TaskQuerySchema,
    TaskSortField,
)


class TaskRepository:

    def __init__(self, db: Session):
        self.db = db

    async def _base_query(self) -> Query:
        return self.db.query(TaskModel).filter(
            TaskModel.deleted_at.is_(None)
        )

    async def _apply_owner_filter(
        self,
        query: Query,
        owner_id: int,
    ) -> Query:
        return query.filter(
            TaskModel.owner_id == owner_id
        )

    async def _apply_search(
        self,
        query: Query,
        search: str | None,
    ) -> Query:
        if not search:
            return query

        search_pattern = f"%{search}%"

        return query.filter(
            or_(
                TaskModel.title.ilike(search_pattern),
                TaskModel.description.ilike(search_pattern),
            )
        )

    async def _apply_filters(
        self,
        query: Query,
        params: TaskQuerySchema,
    ) -> Query:

        if params.is_completed is not None:
            query = query.filter(
                TaskModel.is_completed == params.is_completed
            )

        if params.priority is not None:
            query = query.filter(
                TaskModel.priority == params.priority
            )

        if params.due_from is not None:
            query = query.filter(
                TaskModel.due_date >= params.due_from
            )

        if params.due_to is not None:
            query = query.filter(
                TaskModel.due_date <= params.due_to
            )

        return query

    async def _apply_sorting(
        self,
        query: Query,
        params: TaskQuerySchema,
    ) -> Query:

        sort_fields = {
            TaskSortField.CREATED_AT: TaskModel.created_date,
            TaskSortField.UPDATED_AT: TaskModel.updated_date,
            TaskSortField.DUE_DATE: TaskModel.due_date,
            TaskSortField.PRIORITY: TaskModel.priority,
            TaskSortField.TITLE: TaskModel.title,
        }

        sort_column = sort_fields[params.sort_by]

        if params.order == SortOrder.ASC:
            return query.order_by(sort_column.asc())

        return query.order_by(sort_column.desc())

    async def _apply_pagination(
        self,
        query: Query,
        params: TaskQuerySchema,
    ) -> Query:

        offset = (params.page - 1) * params.page_size

        return query.offset(offset).limit(
            params.page_size
        )

    async def get_tasks(
        self,
        owner_id: int,
        params: TaskQuerySchema,
    ) -> tuple[list[TaskModel], int]:

        query = self._base_query()

        query = self._apply_owner_filter(
            query,
            owner_id,
        )

        query = self._apply_search(
            query,
            params.q,
        )

        query = self._apply_filters(
            query,
            params,
        )

        total = query.count()

        query = self._apply_sorting(
            query,
            params,
        )

        query = self._apply_pagination(
            query,
            params,
        )

        tasks = query.all()

        return tasks, total

    async def get_by_id(
        self,
        task_id: int,
    ) -> TaskModel | None:

        return (
            self._base_query()
            .filter(TaskModel.id == task_id)
            .first()
        )

    async def get_by_id_and_owner_id(
        self,
        task_id: int,
        owner_id: int,
    ) -> TaskModel | None:

        return (
            self._base_query()
            .filter(
                TaskModel.id == task_id,
                TaskModel.owner_id == owner_id,
            )
            .first()
        )

    async def create_task(
        self,
        title: str,
        description: str | None,
        priority: PriorityTypes,
        due_date: datetime | None,
        owner_id: int,
    ) -> TaskModel:

        task = TaskModel(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            owner_id=owner_id,
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return task

    async def update_task(
        self,
        task: TaskModel,
    ) -> TaskModel:

        self.db.commit()
        self.db.refresh(task)

        return task

    async def delete_task(
        self,
        task: TaskModel,
    ) -> None:

        task.deleted_at = datetime.now(timezone.utc)

        self.db.commit()