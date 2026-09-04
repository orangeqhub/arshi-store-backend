from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ProductImageResponse(BaseModel):
    id: str
    image_url: str
    is_primary: bool
    sort_order: int

    class Config:
        from_attributes = True


class ProductSpecificationResponse(BaseModel):
    id: str
    spec_key: str
    spec_value: str

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    id: str
    category_id: Optional[str]
    name: str
    slug: str
    sku: str
    brand: Optional[str]
    short_description: Optional[str]
    mrp: float
    sale_price: float
    stock_qty: int
    thumbnail_url: Optional[str]
    is_featured: bool
    is_bestseller: bool
    is_new_arrival: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProductDetailResponse(BaseModel):
    id: str
    category_id: Optional[str]
    name: str
    slug: str
    sku: str
    brand: Optional[str]

    description: Optional[str]
    short_description: Optional[str]

    mrp: float
    sale_price: float

    stock_qty: int
    thumbnail_url: Optional[str]

    manufacturer: Optional[str]
    hsn_code: Optional[str]

    is_featured: bool
    is_bestseller: bool
    is_new_arrival: bool

    images: List[ProductImageResponse]
    specifications: List[ProductSpecificationResponse]

    created_at: datetime

    class Config:
        from_attributes = True