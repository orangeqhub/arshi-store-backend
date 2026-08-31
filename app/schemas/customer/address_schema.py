from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class AddressCreateRequest(BaseModel):

    full_name: str = Field(
        ...,
        min_length=3,
        max_length=255
    )

    email: EmailStr

    phone: str

    address_line1: str = Field(
        ...,
        min_length=10,
        max_length=500
    )

    address_line2: Optional[str] = Field(
        None,
        max_length=500
    )

    landmark: Optional[str] = Field(
        None,
        max_length=255
    )

    city: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    state: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    pincode: str

    country: str = "India"

    address_type: str = "home"

    is_default: bool = False

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):

        if not value.isdigit():
            raise ValueError(
                "Phone number must contain digits only"
            )

        if len(value) != 10:
            raise ValueError(
                "Phone number must be exactly 10 digits"
            )

        return value

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value):

        if not value.isdigit():
            raise ValueError(
                "Pincode must contain digits only"
            )

        if len(value) != 6:
            raise ValueError(
                "Pincode must be exactly 6 digits"
            )

        return value


class AddressResponse(BaseModel):

    id: UUID

    full_name: str

    email: str

    phone: str

    address_line1: str

    address_line2: Optional[str]

    landmark: Optional[str]

    city: str

    state: str

    pincode: str

    country: str

    address_type: str

    is_default: bool