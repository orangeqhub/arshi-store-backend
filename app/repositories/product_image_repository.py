from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import ProductImage


class ProductImageRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        image: ProductImage
    ):

        db.add(image)

        await db.commit()
        await db.refresh(image)

        return image

    @staticmethod
    async def bulk_create(
        db: AsyncSession,
        images: list[ProductImage]
    ):

        db.add_all(images)

        await db.commit()

        for image in images:
            await db.refresh(image)

        return images

    @staticmethod
    async def get_product_images(
        db: AsyncSession,
        product_id: UUID
    ):

        result = await db.execute(
            select(ProductImage)
            .where(
                ProductImage.product_id == product_id
            )
            .order_by(
                ProductImage.sort_order.asc()
            )
        )

        return result.scalars().all()

    @staticmethod
    async def delete_product_images(
        db: AsyncSession,
        product_id: UUID
    ):

        await db.execute(
            delete(ProductImage).where(
                ProductImage.product_id == product_id
            )
        )

        await db.commit()

        return True

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        image_id: UUID
    ):

        result = await db.execute(
            select(ProductImage).where(
                ProductImage.id == image_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def delete_by_id(
        db: AsyncSession,
        image_id: UUID
    ):

        image = await ProductImageRepository.get_by_id(
            db,
            image_id
        )

        if not image:
            return False

        await db.delete(image)

        await db.commit()

        return True