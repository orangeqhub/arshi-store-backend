from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.schemas.customer.review_schema import (
    CreateReviewRequest
)

from app.services.customer.review_service import (
    ReviewService
)

from app.core.dependencies import (
    get_current_user
)

router = APIRouter(
    prefix="/customer/reviews",
    tags=["Customer Reviews"]
)


@router.post("")
async def create_review(
    payload: CreateReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return await ReviewService.create_review(
        db=db,
        user_id=current_user["sub"],
        payload=payload
    )