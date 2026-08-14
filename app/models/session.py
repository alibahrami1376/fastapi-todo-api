from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from .base import BaseModel


class SessionModel(BaseModel):
    __tablename__ = "sessions"

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    access_token_jti = Column(
        String,
        unique=True,
        nullable=False,
    )

    refresh_token_jti = Column(
        String,
        unique=True,
        nullable=False,
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    user = relationship(
        "UserModel",
        back_populates="sessions",
    )