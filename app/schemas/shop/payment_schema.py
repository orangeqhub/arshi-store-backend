from pydantic import BaseModel


class CreatePaymentResponse(BaseModel):
    order_id: str
    razorpay_order_id: str
    amount: float
    currency: str
    key: str


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str