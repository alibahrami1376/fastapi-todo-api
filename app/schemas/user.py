from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "username": "johndoe123",
                    "email": "user@example.com",
                    "is_active": True,
                    "is_verified": False,
                    "created_date": "2026-08-19T10:00:00+03:30",
                    "updated_date": "2026-08-19T10:00:00+03:30",
                }
            ]
        },
    )

    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_verified: bool
    created_date: datetime
    updated_date: datetime


class UserUpdateSchema(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
