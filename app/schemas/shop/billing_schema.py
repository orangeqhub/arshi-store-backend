from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel


class CreatePaymentRequest(BaseModel):
    order_id: UUID


class CreatePaymentResponse(BaseModel):
    order_id: UUID
    razorpay_order_id: str
    amount: int
    currency: str
    razorpay_key: str


class VerifyPaymentRequest(BaseModel):
    order_id: UUID
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class VerifyPaymentResponse(BaseModel):
    success: bool
    message: str


class PaymentResponse(BaseModel):
    id: UUID
    amount: Decimal
    status: str
    gateway_order_id: str | None = None
    gateway_transaction_id: str | None = None