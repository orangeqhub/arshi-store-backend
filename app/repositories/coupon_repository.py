from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Coupon,
    CouponUsage
)


class CouponRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        coupon: Coupon
    ):
        db.add(coupon)

        await db.commit()
        await db.refresh(coupon)

        return coupon

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        coupon_id: UUID
    ):
        result = await db.execute(
            select(Coupon)
            .where(
                Coupon.id == coupon_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_code(
        db: AsyncSession,
        coupon_code: str
    ):
        result = await db.execute(
            select(Coupon)
            .where(
                Coupon.code == coupon_code
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession
    ):
        result = await db.execute(
            select(Coupon)
            .order_by(
                Coupon.created_at.desc()
            )
        )

        return result.scalars().all()

    @staticmethod
    async def update(
        db: AsyncSession,
        coupon
    ):
        await db.commit()

        await db.refresh(coupon)

        return coupon

    @staticmethod
    async def delete(
        db: AsyncSession,
        coupon
    ):
        await db.delete(coupon)

        await db.commit()

    @staticmethod
    async def get_active_coupons(
        db: AsyncSession
    ):
        result = await db.execute(
            select(Coupon)
            .where(
                Coupon.is_active == True,
                Coupon.valid_from <= datetime.utcnow(),
                Coupon.valid_until >= datetime.utcnow()
            )
        )

        return result.scalars().all()

    @staticmethod
    async def has_user_used_coupon(
        db: AsyncSession,
        user_id: UUID,
        coupon_id: UUID
    ):
        result = await db.execute(
            select(CouponUsage)
            .where(
                CouponUsage.user_id == user_id,
                CouponUsage.coupon_id == coupon_id
            )
            .limit(1)
        )

        return result.scalar_one_or_none()
    


    @staticmethod
    async def validate_coupon(
        db,
        coupon_code
    ):

        coupon = await CouponRepository.get_by_code(
            db,
            coupon_code
        )

        if not coupon:
            return None

        if not coupon.is_active:
            return None

        current_time = datetime.utcnow()

        if current_time < coupon.valid_from:
            return None

        if current_time > coupon.valid_until:
            return None

        if (
            coupon.usage_limit
            and
            coupon.used_count >= coupon.usage_limit
        ):
            return None

        return coupon
    
    @staticmethod
    async def get_coupon_by_code(
        db,
        code: str
    ):
        result = await db.execute(
            select(Coupon)
            .where(
                Coupon.code == code,
                Coupon.is_active == True
            )
        )

        return result.scalar_one_or_none()