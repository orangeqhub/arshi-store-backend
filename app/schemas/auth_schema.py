from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class AdminRegisterRequest(BaseModel):
    full_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Full name of the admin"
    )

    email: EmailStr

    phone: str = Field(
        ...,
        pattern=r"^[6-9]\d{9}$",
        description="Valid 10-digit Indian mobile number"
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=50,
        description="Password must be strong"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )

        if not re.search(r"[a-z]", value):
            raise ValueError(
                "Password must contain at least one lowercase letter"
            )

        if not re.search(r"\d", value):
            raise ValueError(
                "Password must contain at least one number"
            )

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError(
                "Password must contain at least one special character"
            )

        return value


class UserRegisterRequest(BaseModel):
    full_name: str = Field(
        ...,
        min_length=3,
        max_length=100
    )

    email: EmailStr

    phone: str = Field(
        ...,
        pattern=r"^[6-9]\d{9}$"
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=50
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )

        if not re.search(r"[a-z]", value):
            raise ValueError(
                "Password must contain at least one lowercase letter"
            )

        if not re.search(r"\d", value):
            raise ValueError(
                "Password must contain at least one number"
            )

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError(
                "Password must contain at least one special character"
            )

        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str