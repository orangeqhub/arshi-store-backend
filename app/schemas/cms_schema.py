from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SiteContentUpdate(BaseModel):
    content: dict = Field(default_factory=dict)


class BannerCreate(BaseModel):
    title: str
    subtitle: str | None = None
    image_url: str
    mobile_image_url: str | None = None
    redirect_url: str | None = None
    sort_order: int = 0
    is_active: bool = True


class BannerUpdate(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    image_url: str | None = None
    mobile_image_url: str | None = None
    redirect_url: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class BlogPostCreate(BaseModel):
    title: str
    excerpt: str | None = None
    content: str | None = None
    category: str | None = None
    image_url: str | None = None
    sort_order: int = 0
    is_active: bool = True
    published_at: datetime | None = None


class BlogPostUpdate(BaseModel):
    title: str | None = None
    excerpt: str | None = None
    content: str | None = None
    category: str | None = None
    image_url: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None
    published_at: datetime | None = None


class GalleryImageCreate(BaseModel):
    image_url: str
    alt_text: str | None = None
    link_url: str | None = None
    sort_order: int = 0
    is_active: bool = True


class GalleryImageUpdate(BaseModel):
    image_url: str | None = None
    alt_text: str | None = None
    link_url: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class HomepageFeatureCreate(BaseModel):
    title: str
    description: str | None = None
    icon_name: str | None = None
    color: str | None = None
    sort_order: int = 0
    is_active: bool = True


class HomepageFeatureUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    icon_name: str | None = None
    color: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class NewsletterSubscribeRequest(BaseModel):
    email: EmailStr


class BannerResponse(BaseModel):
    id: UUID
    title: str
    subtitle: str | None
    image_url: str
    mobile_image_url: str | None
    redirect_url: str | None
    sort_order: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
