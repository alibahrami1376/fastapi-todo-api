import re

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from core.exceptions import CustomValidationException
from messages import AuthMessages



class RegisterRequestSchema(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=72,
        examples=["a/@1234567"],
    )
    confirm_password: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "StrongPass@123",
                    "confirm_password": "StrongPass@123",
                }
            ]
        }
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Validate password complexity requirements."""

        if not re.search(r"[A-Z]", value):
            raise CustomValidationException(
                AuthMessages.password_one_uppercase
            )

        if not re.search(r"[a-z]", value):
            raise CustomValidationException(
                AuthMessages.password_one_lowercase
            )

        if not re.search(r"\d", value):
            raise CustomValidationException(
                AuthMessages.password_one_digit
            )

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise CustomValidationException(
                AuthMessages.password_special_char
            )

        return value

    @model_validator(mode="after")
    def check_password_match(self) -> "RegisterRequestSchema":
        """Ensure passwords match."""

        if self.password != self.confirm_password:
            raise CustomValidationException(
                AuthMessages.passwords_do_not_match
            )

        return self


class LoginRequestSchema(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        examples=["a/@1234567"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "StrongPass@123",
                }
            ]
        }
    )


class LoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterResponseSchema(BaseModel):
    user_id: int
    email: EmailStr
    detail: str

class RefreshTokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"