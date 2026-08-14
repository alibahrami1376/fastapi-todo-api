from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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