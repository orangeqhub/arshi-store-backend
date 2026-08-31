from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category_repository import CategoryRepository


class CategoryService:

    @staticmethod
    async def get_categories(db: AsyncSession):
        categories = await CategoryRepository.get_active_all(db)

        return {
            "success": True,
            "status_code": 200,
            "message": "Categories fetched successfully",
            "data": [
                {
                    "id": str(category.id),
                    "name": category.name,
                    "icon": category.icon or "🌿",
                    "slug": category.slug,
                    "description": category.description,
                    "image_url": category.image_url,
                    "parent_id": str(category.parent_id) if category.parent_id else None,
                }
                for category in categories
            ],
        }
