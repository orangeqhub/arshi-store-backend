from uuid import UUID

from pydantic import BaseModel

from app.models.models import PaymentMethod


class CreateOrderRequest(BaseModel):

    address_id: UUID

    payment_method: PaymentMethod

    coupon_code: str | None = None


class PaymentSuccessRequest(BaseModel):

    order_id: UUID

    transaction_id: str


class CancelOrderRequest(BaseModel):

    reason: str