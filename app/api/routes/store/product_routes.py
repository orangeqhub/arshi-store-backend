from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.store.product_service import ProductService

router = APIRouter(
    prefix="/store/products",
    tags=["Products"]
)


@router.get("")
async def get_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    category_id: UUID | None = Query(None),
    category_name: str | None = Query(None),
    is_featured: bool | None = Query(None),
    is_bestseller: bool | None = Query(None),
    is_new_arrival: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await ProductService.get_products(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        category_name=category_name,
        is_featured=is_featured,
        is_bestseller=is_bestseller,
        is_new_arrival=is_new_arrival,
    )


@router.get("/{product_id}")
async def get_product_details(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await ProductService.get_product_details(
        db=db,
        product_id=product_id,
    )
