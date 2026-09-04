from uuid import UUID
from typing import Optional
from pydantic import BaseModel

from app.models.models import (
    OrderStatus,
    PaymentStatus
)


class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus


class UpdatePaymentStatusRequest(BaseModel):
    payment_status: PaymentStatus


class CancelOrderRequest(BaseModel):
    reason: str


class OrderFilters(BaseModel):
    search: Optional[str] = None
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None