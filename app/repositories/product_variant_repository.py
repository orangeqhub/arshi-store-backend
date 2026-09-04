from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import ProductVariant


class ProductVariantRepository:

    @staticmethod
    async def get_by_sku(
        db: AsyncSession,
        sku: str
    ):

        result = await db.execute(
            select(ProductVariant)
            .where(ProductVariant.sku == sku)
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        variant_id: UUID
    ):

        result = await db.execute(
            select(ProductVariant)
            .where(ProductVariant.id == variant_id)
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_product(
        db: AsyncSession,
        product_id: UUID
    ):

        result = await db.execute(
            select(ProductVariant)
            .where(ProductVariant.product_id == product_id)
            .order_by(ProductVariant.sort_order)
        )

        return result.scalars().all()

    @staticmethod
    async def bulk_create(
        db: AsyncSession,
        variants: list[ProductVariant]
    ):

        db.add_all(variants)

        await db.flush()

        return variants

    @staticmethod
    async def delete(
        db: AsyncSession,
        variant: ProductVariant
    ):

        await db.delete(variant)
