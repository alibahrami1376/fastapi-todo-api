import secrets
import string

from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from .base import BaseModel


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


class UsernameMixin:
    username: str

    @classmethod
    def generate_random_username(cls, length: int = 10) -> str:
        """Generate a random username using lowercase letters and digits."""
        characters = string.ascii_lowercase + string.digits

        return "".join(
            secrets.choice(characters)
            for _ in range(length)
        )


class PasswordMixin:
    password: str

    def verify_password(self, plain_password: str) -> bool:
        """Verify a plain-text password against the stored hash."""
        return pwd_context.verify(
            plain_password,
            self.password,
        )

    def set_password(self, plain_text: str) -> None:
        """Hash and store a plain-text password."""
        self.password = pwd_context.hash(plain_text)


class UserModel(PasswordMixin, UsernameMixin, BaseModel):
    __tablename__ = "users"

    username = Column(
        String,
        unique=True,
        nullable=False,
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
    )

    password = Column(
        String,
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
    )

    is_verified = Column(
        Boolean,
        default=False,
    )

    tasks = relationship(
        "TaskModel",
        back_populates="owner",
    )

    sessions = relationship(
    "SessionModel",
    back_populates="user",
    )