from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends,Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.services.customer.wishlist_service import (
    WishlistService
)

router = APIRouter(
    prefix="/customer/wishlist",
    tags=["Wishlist"]
)


@router.post("/{product_id}")
async def add_to_wishlist(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return await WishlistService.add_to_wishlist(
        db=db,
        user_id=current_user["sub"],
        product_id=product_id
    )


@router.get("")
async def get_wishlist(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return await WishlistService.get_wishlist(
        db=db,
        user_id=current_user["sub"],
        page=page,
        page_size=page_size
    )

@router.delete("/{product_id}")
async def remove_from_wishlist(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return await WishlistService.remove_from_wishlist(
        db=db,
        user_id=current_user["sub"],
        product_id=product_id
    )