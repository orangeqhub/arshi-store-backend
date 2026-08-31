from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.schemas.customer.order_schema import (
    CreateOrderRequest,
    PaymentSuccessRequest,
    CancelOrderRequest
)

from app.services.customer.order_service import (
    OrderService
)

router = APIRouter(
    prefix="/customer/orders",
    tags=["Orders"]
)


@router.post("")
async def create_order(
    payload: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return await OrderService.create_order(
        db=db,
        user_id=current_user["sub"],
        payload=payload
    )


@router.post("/payment-success")
async def payment_success(
    payload: PaymentSuccessRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return await OrderService.payment_success(
        db=db,
        user_id=current_user["sub"],
        payload=payload
    )


@router.get("")
async def get_orders(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return await OrderService.get_orders(
        db=db,
        user_id=current_user["sub"]
    )


@router.get("/{order_id}")
async def get_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return await OrderService.get_order(
        db=db,
        user_id=current_user["sub"],
        order_id=order_id
    )


@router.get("/{order_id}/tracking")
async def get_order_tracking(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return await OrderService.track_shipment(
        db=db,
        user_id=current_user["sub"],
        order_id=order_id
    )


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: UUID,
    payload: CancelOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return await OrderService.cancel_order(
        db=db,
        user_id=current_user["sub"],
        order_id=order_id,
        reason=payload.reason
    )