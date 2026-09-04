from uuid import UUID
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict
)


class CategoryCreate(BaseModel):

    name: str

    description: str | None = None

    icon: str | None = None

    image_url: str | None = None

    parent_id: UUID | None = None

    is_active: bool = True


class CategoryUpdate(BaseModel):

    name: str | None = None

    description: str | None = None

    icon: str | None = None

    image_url: str | None = None

    parent_id: UUID | None = None

    is_active: bool | None = None


class CategoryResponse(BaseModel):

    id: UUID

    name: str

    slug: str

    icon: str | None = None

    description: str | None = None

    image_url: str | None = None

    parent_id: UUID | None = None

    is_active: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )