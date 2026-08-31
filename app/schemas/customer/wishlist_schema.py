from uuid import UUID
from pydantic import BaseModel


class WishlistAddResponse(BaseModel):
    product_id: UUID


class WishlistProductResponse(BaseModel):
    id: UUID
    product_id: UUID
    name: str
    slug: str
    sku: str
    sale_price: float
    mrp: float
    thumbnail_url: str | None
    stock_qty: int