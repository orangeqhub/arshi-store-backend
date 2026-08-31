from uuid import UUID
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from enum import Enum
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class CouponType(str, Enum):
    PERCENTAGE = "percentage"
    FLAT = "flat"
    FREE_SHIPPING = "free_shipping"


class CouponCreate(BaseModel):
    code: str
    title: str
    description: str | None = None

    coupon_type: CouponType

    discount_value: float
    max_discount_amount: float | None = None
    minimum_order_amount: float = 0
    usage_limit: int | None = None

    is_first_order_only: bool = False

    valid_from: datetime
    valid_until: datetime

    product_ids: list[UUID] = []
    category_ids: list[UUID] = []


class CouponUpdate(BaseModel):

    title: str | None = None

    description: str | None = None

    discount_value: Decimal | None = None

    max_discount_amount: Decimal | None = None

    minimum_order_amount: Decimal | None = None

    usage_limit: int | None = None

    is_active: bool | None = None

    is_first_order_only: bool | None = None

    valid_from: datetime | None = None

    valid_until: datetime | None = None


class CouponStatusUpdate(BaseModel):

    is_active: bool


class CouponResponse(BaseModel):

    id: UUID

    code: str

    title: str

    coupon_type: str

    discount_value: Decimal

    minimum_order_amount: Decimal

    usage_limit: int | None

    used_count: int

    is_active: bool

    valid_from: datetime

    valid_until: datetime