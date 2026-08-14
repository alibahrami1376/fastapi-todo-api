from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import PriorityTypes


class TodoCreateSchema(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
    )
    due_date: datetime | None = None
    priority: PriorityTypes = PriorityTypes.LOW

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: datetime | None) -> datetime | None:
        if value and value < datetime.now(timezone.utc):
            raise ValueError("Due date cannot be in the past.")

        return value


class TodoUpdateSchema(BaseModel):
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
    due_date: datetime | None = None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: datetime | None) -> datetime | None:
        if value and value < datetime.now(timezone.utc):
            raise ValueError("Due date cannot be in the past.")

        return value


class TodoResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    is_completed: bool
    priority: PriorityTypes
    due_date: datetime | None
    owner_id: int
    created_date: datetime
    updated_date: datetime