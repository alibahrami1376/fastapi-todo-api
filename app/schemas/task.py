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

    @field_validator("due_date")
    @classmethod
    def validate_due_date_field(cls, value: date | None) -> date | None:
        return validate_due_date(value)


class TaskResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
