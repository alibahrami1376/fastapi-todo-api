from enum import Enum

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from .base import BaseModel


class PriorityTypes(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskModel(BaseModel):
    __tablename__ = "tasks"

    title = Column(
        String,
        nullable=False,
    )

    description = Column(
        String,
        nullable=True,
    )

    is_completed = Column(
        Boolean,
        default=False,
    )

    priority = Column(
        SQLEnum(PriorityTypes),
        nullable=False,
        default=PriorityTypes.LOW,
    )

    due_date = Column(
        Date,
        nullable=True,
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    owner = relationship(
        "UserModel",
        back_populates="tasks",
    )
