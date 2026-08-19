from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
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

    access_expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    refresh_expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    fingerprint_hash = Column(
        String,
        nullable=True,
    )

    access_revoked_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    refresh_revoked_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    user = relationship(
        "UserModel",
        back_populates="sessions",
    )
