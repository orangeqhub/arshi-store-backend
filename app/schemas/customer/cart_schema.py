from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


class AddToCartRequest(BaseModel):

    variant_id: UUID | None = None

    quantity: int = Field(
        default=1,
        ge=1
    )


class ApplyCouponRequest(BaseModel):

    coupon_code: str