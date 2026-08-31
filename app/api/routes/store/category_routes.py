from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.store.category_service import CategoryService

router = APIRouter(
    prefix="/store/categories",
    tags=["Categories"]
)


@router.get("")
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    return await CategoryService.get_categories(db)