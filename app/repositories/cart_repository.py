from uuid import UUID

from sqlalchemy import select
from sqlalchemy import func

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import joinedload

from app.models.models import (
    CartItem,
    Product
)
from sqlalchemy import select
from sqlalchemy.orm import joinedload






class CartRepository:

    @staticmethod
    async def get_by_user_and_product(
        db: AsyncSession,
        user_id: UUID,
        product_id: UUID
    ):

        result = await db.execute(
            select(CartItem)
            .where(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        cart_item: CartItem
    ):

        db.add(cart_item)

        await db.commit()
        await db.refresh(cart_item)

        return cart_item

    @staticmethod
    async def update(
        db: AsyncSession,
        cart_item: CartItem
    ):

        await db.commit()
        await db.refresh(cart_item)

        return cart_item

    @staticmethod
    async def get_cart_items(
        db: AsyncSession,
        user_id: UUID,
        page: int,
        page_size: int
    ):

        count_result = await db.execute(
            select(func.count(CartItem.id))
            .where(
                CartItem.user_id == user_id
            )
        )

        total_records = count_result.scalar() or 0

        result = await db.execute(
            select(CartItem)
            .options(
                joinedload(CartItem.product)
                .joinedload(Product.images),

                joinedload(CartItem.product)
                .joinedload(Product.category)
            )
            .where(
                CartItem.user_id == user_id
            )
            .order_by(
                CartItem.created_at.desc()
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        return (
            result.unique().scalars().all(),
            total_records
        )

    @staticmethod
    async def delete(
        db: AsyncSession,
        cart_item: CartItem
    ):

        await db.delete(cart_item)

        await db.commit()


    @staticmethod
    async def get_all_cart_items(
        db,
        user_id
    ):

        result = await db.execute(
            select(CartItem)
            .options(
                joinedload(CartItem.product)
                .joinedload(Product.category),

                joinedload(CartItem.product)
                .joinedload(Product.images)
            )
            .where(
                CartItem.user_id == user_id
            )
        )

        return result.unique().scalars().all()