from pydantic import BaseModel
from pydantic import Field


class AddToCartRequest(BaseModel):

    quantity: int = Field(
        default=1,
        ge=1
    )


class ApplyCouponRequest(BaseModel):

    coupon_code: str