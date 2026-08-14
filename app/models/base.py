from datetime import datetime

from core.database import Base
from sqlalchemy import Column, DateTime, func, Integer


class BaseModel(Base):
    __abstract__ = True

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    created_date = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        default=None
    )

    def soft_delete(self):
        self.deleted_at = datetime.now()

    def restore(self):
        self.deleted_at = None