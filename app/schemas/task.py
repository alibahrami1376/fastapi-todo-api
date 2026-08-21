from datetime import date, datetime
from enum import Enum
from zoneinfo import ZoneInfo

from core.config import settings
from models import PriorityTypes
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def validate_due_date(value: date | None) -> date | None:
    if value is None:
        return None

    if value < datetime.now(ZoneInfo(settings.TIMEZONE)).date():
        raise ValueError("Due date cannot be in the past.")

    return value


class TaskCreateSchema(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
    )
    due_date: date | None = None
    priority: PriorityTypes = PriorityTypes.LOW

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Finish project report",
                    "description": "Complete the weekly status report",
                    "priority": "high",
                    "due_date": "2026-08-31",
                }
            ]
        }
    )

    @field_validator("due_date")
    @classmethod
    def validate_due_date_field(cls, value: date | None) -> date | None:
        return validate_due_date(value)


class TaskUpdateSchema(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
    )
    is_completed: bool | None = None
    priority: PriorityTypes | None = None
    due_date: date | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Updated task title",
                    "is_completed": True,
                }
            ]
        }
    )

    @field_validator("due_date")
    @classmethod
    def validate_due_date_field(cls, value: date | None) -> date | None:
        return validate_due_date(value)


class TaskResponseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "title": "Finish project report",
                    "description": "Complete the weekly status report",
                    "is_completed": False,
                    "priority": "high",
                    "due_date": "2026-08-31",
                    "owner_id": 1,
                    "created_date": "2026-08-19T10:00:00+03:30",
                    "updated_date": "2026-08-19T10:00:00+03:30",
                }
            ]
        },
    )

    id: int
    title: str
    description: str | None
    is_completed: bool
    priority: PriorityTypes
    due_date: date | None
    owner_id: int
    created_date: datetime
    updated_date: datetime


class TaskListResponseSchema(BaseModel):
    results: list[TaskResponseSchema]
    page: int
    page_size: int
    total: int
    pages: int

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "results": [
                        {
                            "id": 1,
                            "title": "Finish project report",
                            "description": "Complete the weekly status report",
                            "is_completed": False,
                            "priority": "high",
                            "due_date": "2026-08-31",
                            "owner_id": 1,
                            "created_date": "2026-08-19T10:00:00+03:30",
                            "updated_date": "2026-08-19T10:00:00+03:30",
                        }
                    ],
                    "page": 1,
                    "page_size": 10,
                    "total": 1,
                    "pages": 1,
                }
            ]
        }
    )


class TaskPriorityStatsSchema(BaseModel):
    low: int = 0
    medium: int = 0
    high: int = 0


class TaskStatsResponseSchema(BaseModel):
    total: int
    completed: int
    pending: int
    overdue: int
    by_priority: TaskPriorityStatsSchema

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "total": 10,
                    "completed": 4,
                    "pending": 6,
                    "overdue": 2,
                    "by_priority": {
                        "low": 3,
                        "medium": 5,
                        "high": 2,
                    },
                }
            ]
        }
    )


class TaskBulkIdsSchema(BaseModel):
    ids: list[int] = Field(
        min_length=1,
        max_length=50,
        description="Task IDs to process (1–50 items).",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "ids": [1, 2, 3],
                }
            ]
        }
    )

    @field_validator("ids")
    @classmethod
    def validate_ids(cls, value: list[int]) -> list[int]:
        if any(task_id < 1 for task_id in value):
            raise ValueError("All task ids must be positive integers.")

        # Preserve order, drop duplicates
        unique: list[int] = []
        seen: set[int] = set()
        for task_id in value:
            if task_id not in seen:
                seen.add(task_id)
                unique.append(task_id)
        return unique


class TaskBulkCompleteResponseSchema(BaseModel):
    updated: int
    ids: list[int]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "updated": 3,
                    "ids": [1, 2, 3],
                }
            ]
        }
    )


class TaskBulkDeleteResponseSchema(BaseModel):
    deleted: int
    ids: list[int]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "deleted": 3,
                    "ids": [1, 2, 3],
                }
            ]
        }
    )


class TaskPutSchema(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=100,
    )

    description: str = Field(
        max_length=1000,
    )

    is_completed: bool

    priority: PriorityTypes

    due_date: date | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Finish project report",
                    "description": "Complete the weekly status report",
                    "is_completed": True,
                    "priority": "high",
                    "due_date": "2026-08-31",
                }
            ]
        }
    )

    @field_validator("due_date")
    @classmethod
    def validate_due_date_field(cls, value: date | None) -> date | None:
        return validate_due_date(value)


class TaskSortField(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    DUE_DATE = "due_date"
    PRIORITY = "priority"
    TITLE = "title"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class TaskQuerySchema(BaseModel):
    q: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    is_completed: bool | None = None

    priority: PriorityTypes | None = None

    due_from: date | None = None

    due_to: date | None = None

    sort_by: TaskSortField = TaskSortField.CREATED_AT

    order: SortOrder = SortOrder.DESC

    page: int = Field(
        default=1,
        ge=1,
    )

    page_size: int = Field(
        default=10,
        ge=1,
        le=50,
    )

    @model_validator(mode="after")
    def validate_due_range(self):
        if (
            self.due_from is not None
            and self.due_to is not None
            and self.due_to < self.due_from
        ):
            raise ValueError("due_to cannot be earlier than due_from.")

        return self
