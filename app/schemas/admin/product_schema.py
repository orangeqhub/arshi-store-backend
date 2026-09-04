from uuid import UUID
from decimal import Decimal
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class ProductVariantCreate(BaseModel):

    label: str

    weight_grams: int | None = None
    size_value: str | None = None

    sku: str

    mrp: Decimal = Field(gt=0)
    sale_price: Decimal = Field(gt=0)

    stock_qty: int = Field(default=0, ge=0)

    is_active: bool = True
    is_default: bool = False

    sort_order: int = 0


class ProductVariantUpdate(BaseModel):

    id: UUID | None = None

    label: str

    weight_grams: int | None = None
    size_value: str | None = None

    sku: str

    mrp: Decimal = Field(gt=0)
    sale_price: Decimal = Field(gt=0)

    stock_qty: int = Field(default=0, ge=0)

    is_active: bool = True
    is_default: bool = False

    sort_order: int = 0


class ProductVariantResponse(BaseModel):

    id: UUID

    label: str

    weight_grams: int | None = None
    size_value: str | None = None

    sku: str

    mrp: Decimal
    sale_price: Decimal

    stock_qty: int

    is_active: bool
    is_default: bool

    sort_order: int = 0

    model_config = ConfigDict(
        from_attributes=True
    )


class ProductCreate(BaseModel):

    category_id: UUID

    name: str
    sku: str

    brand: str | None = None

    description: str | None = None
    short_description: str | None = None

    mrp: Decimal = Field(
        gt=0
    )

    sale_price: Decimal = Field(
        gt=0
    )

    stock_qty: int = Field(
        default=0,
        ge=0
    )

    manufacturer: str | None = None

    hsn_code: str | None = None

    is_featured: bool = False
    is_bestseller: bool = False
    is_new_arrival: bool = False

    variants: list[ProductVariantCreate] = []


class ProductUpdate(BaseModel):

    category_id: UUID | None = None

    name: str | None = None

    sku: str | None = None

    brand: str | None = None

    description: str | None = None

    short_description: str | None = None

    mrp: Decimal | None = Field(
        default=None,
        gt=0
    )

    sale_price: Decimal | None = Field(
        default=None,
        gt=0
    )

    stock_qty: int | None = Field(
        default=None,
        ge=0
    )

    manufacturer: str | None = None

    hsn_code: str | None = None

    is_featured: bool | None = None

    is_bestseller: bool | None = None

    is_new_arrival: bool | None = None

    variants: list[ProductVariantUpdate] | None = None


class ProductImageResponse(BaseModel):

    id: UUID | None = None

    image_url: str

    is_primary: bool = False

    sort_order: int = 0

    model_config = ConfigDict(
        from_attributes=True
    )


class ProductResponse(BaseModel):

    id: UUID

    category_id: UUID | None = None

    category_name: str | None = None

    name: str

    slug: str

    sku: str

    brand: str | None = None

    description: str | None = None

    short_description: str | None = None

    mrp: Decimal

    sale_price: Decimal

    discount_percentage: int = 0

    stock_qty: int

    stock_status: str | None = None

    thumbnail_url: str | None = None

    manufacturer: str | None = None

    hsn_code: str | None = None

    rating: float = 0

    review_count: int = 0

    is_featured: bool

    is_bestseller: bool

    is_new_arrival: bool

    images: list[ProductImageResponse] = []

    variants: list[ProductVariantResponse] = []

    created_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )