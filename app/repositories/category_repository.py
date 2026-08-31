from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Category


class CategoryRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        category: Category
    ):

        db.add(category)

        await db.commit()

        await db.refresh(category)

        return category

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        category_id: UUID
    ):

        result = await db.execute(
            select(Category).where(
                Category.id == category_id,
                Category.is_deleted == False
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_slug(
        db: AsyncSession,
        slug: str
    ):

        result = await db.execute(
            select(Category).where(
                Category.slug == slug,
                Category.is_deleted == False
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession
    ):

        result = await db.execute(
            select(Category)
            .where(
                Category.is_deleted == False
            )
            .order_by(Category.name.asc())
        )

        return result.scalars().all()

    @staticmethod
    async def get_active_all(
        db: AsyncSession
    ):

        result = await db.execute(
            select(Category)
            .where(
                Category.is_deleted == False,
                Category.is_active == True,
            )
            .order_by(Category.name.asc())
        )

        return result.scalars().all()

    @staticmethod
    async def get_by_name(
        db: AsyncSession,
        name: str
    ):

        result = await db.execute(
            select(Category).where(
                Category.name.ilike(name),
                Category.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def update(
        db: AsyncSession,
        category: Category
    ):

        await db.commit()

        await db.refresh(category)

        return category

    @staticmethod
    async def delete(
        db: AsyncSession,
        category: Category
    ):

        category.is_deleted = True

        await db.commit()

        return True