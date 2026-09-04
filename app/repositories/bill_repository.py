from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Order,
    Payment
)


class BillRepository:

    @staticmethod
    async def get_order(
        db: AsyncSession,
        order_id: UUID
    ):
        result = await db.execute(
            select(Order).where(
                Order.id == order_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_payment_by_order(
        db: AsyncSession,
        order_id: UUID
    ):
        result = await db.execute(
            select(Payment).where(
                Payment.order_id == order_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def save(
        db: AsyncSession
    ):
        await db.commit()

    @staticmethod
    async def refresh(
        db: AsyncSession,
        obj
    ):
        await db.refresh(obj)