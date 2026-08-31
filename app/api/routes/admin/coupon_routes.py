from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.core.dependencies import (
    get_current_admin
)

from app.schemas.admin.coupon_schema import (
    CouponCreate,
    CouponUpdate,
    CouponStatusUpdate
)

from app.services.admin.coupon_service import (
    CouponService
)

router = APIRouter(
    prefix="/admin/coupons",
    tags=["Admin Coupons"]
)


@router.post("")
async def create_coupon(
    payload: CouponCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    return await CouponService.create_coupon(
        db,
        payload
    )


@router.get("")
async def get_coupons(
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    return await CouponService.get_coupons(
        db
    )


@router.get("/{coupon_id}")
async def get_coupon(
    coupon_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    return await CouponService.get_coupon(
        db,
        coupon_id
    )


@router.put("/{coupon_id}")
async def update_coupon(
    coupon_id: UUID,
    payload: CouponUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    return await CouponService.update_coupon(
        db,
        coupon_id,
        payload
    )


@router.patch("/{coupon_id}/status")
async def update_coupon_status(
    coupon_id: UUID,
    payload: CouponStatusUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    return await CouponService.update_coupon_status(
        db,
        coupon_id,
        payload.is_active
    )


@router.delete("/{coupon_id}")
async def delete_coupon(
    coupon_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    return await CouponService.delete_coupon(
        db,
        coupon_id
    )