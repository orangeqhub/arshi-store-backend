from uuid import UUID

from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from slugify import slugify

from app.models.models import Category

from app.repositories.category_repository import (
    CategoryRepository
)

class CategoryService:

    @staticmethod
    async def create_category(
        db: AsyncSession,
        name: str,
        description: str | None,
        icon: str | None,
        image_url: str | None,
        parent_id: UUID | None,
        is_active: bool
    ):

        try:

            slug = slugify(name)

            existing = await CategoryRepository.get_by_slug(
                db,
                slug
            )

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Category already exists"
                )

            if parent_id:

                parent = await CategoryRepository.get_by_id(
                    db,
                    parent_id
                )

                if not parent:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Parent category not found"
                    )

            category = Category(
                name=name,
                slug=slug,
                icon=icon or "🌿",
                description=description,
                image_url=image_url,
                parent_id=parent_id,
                is_active=is_active
            )

            return await CategoryRepository.create(
                db,
                category
            )

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    @staticmethod
    async def get_category(
        db: AsyncSession,
        category_id: UUID
    ):

        category = await CategoryRepository.get_by_id(
            db,
            category_id
        )

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

        return category

    @staticmethod
    async def get_categories(
        db: AsyncSession
    ):

        return await CategoryRepository.get_all(
            db
        )

    @staticmethod
    async def update_category(
        db: AsyncSession,
        category_id: UUID,
        payload
    ):

        try:

            category = await CategoryRepository.get_by_id(
                db,
                category_id
            )

            if not category:
                raise HTTPException(
                    status_code=404,
                    detail="Category not found"
                )

            update_data = payload.model_dump(
                exclude_unset=True
            )

            if "name" in update_data:

                new_name = update_data["name"]

                slug = slugify(
                    new_name
                )

                existing = await CategoryRepository.get_by_slug(
                    db,
                    slug
                )

                if (
                    existing and
                    existing.id != category.id
                ):
                    raise HTTPException(
                        status_code=409,
                        detail="Category name already exists"
                    )

                category.name = new_name
                category.slug = slug

            if "icon" in update_data:
                category.icon = update_data["icon"]

            if "image_url" in update_data:
                category.image_url = update_data["image_url"]

            if (
                "parent_id" in update_data
                and update_data["parent_id"]
            ):

                parent = await CategoryRepository.get_by_id(
                    db,
                    update_data["parent_id"]
                )

                if not parent:
                    raise HTTPException(
                        status_code=404,
                        detail="Parent category not found"
                    )

            if "description" in update_data:
                category.description = update_data["description"]

            if "parent_id" in update_data:
                category.parent_id = update_data["parent_id"]

            if "is_active" in update_data:
                category.is_active = update_data["is_active"]

            return await CategoryRepository.update(
                db,
                category
            )

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    @staticmethod
    async def delete_category(
        db: AsyncSession,
        category_id: UUID
    ):

        category = await CategoryRepository.get_by_id(
            db,
            category_id
        )

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

        await CategoryRepository.delete(
            db,
            category
        )

        return {
            "success": True,
            "status_code": 200,
            "message": "Category deleted successfully"
        }