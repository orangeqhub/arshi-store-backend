from uuid import UUID





from fastapi import (
    APIRouter,
    Depends,
    Query
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.core.dependencies import (
    get_current_admin
)

from app.schemas.admin.review_schema import (
    ReviewActionRequest
)

from app.services.admin.review_service import (
    AdminReviewService
)

router = APIRouter(
    prefix="/admin/reviews",
    tags=["Admin Reviews"],
    dependencies=[Depends(get_current_admin)]
)


@router.get("")
async def get_reviews(
    status: str | None = Query(None),
    page: int = Query(1),
    page_size: int = Query(20),
    db: AsyncSession = Depends(get_db)
):

    return await AdminReviewService.get_reviews(
        db=db,
        status=status,
        page=page,
        page_size=page_size
    )


@router.get("/dashboard")
async def dashboard(
    db: AsyncSession = Depends(get_db)
):

    return await AdminReviewService.dashboard(
        db=db
    )


@router.get("/{review_id}")
async def get_review(
    review_id: UUID,
    db: AsyncSession = Depends(get_db)
):

    return await AdminReviewService.get_review(
        db=db,
        review_id=review_id
    )


@router.patch("/{review_id}/approve")
async def approve_review(
    review_id: UUID,
    payload: ReviewActionRequest,
    db: AsyncSession = Depends(get_db)
):

    return await AdminReviewService.approve_review(
        db=db,
        review_id=review_id,
        admin_note=payload.admin_note
    )


@router.patch("/{review_id}/reject")
async def reject_review(
    review_id: UUID,
    payload: ReviewActionRequest,
    db: AsyncSession = Depends(get_db)
):

    return await AdminReviewService.reject_review(
        db=db,
        review_id=review_id,
        admin_note=payload.admin_note
    )


@router.patch("/{review_id}/flag")
async def flag_review(
    review_id: UUID,
    payload: ReviewActionRequest,
    db: AsyncSession = Depends(get_db)
):

    return await AdminReviewService.flag_review(
        db=db,
        review_id=review_id,
        admin_note=payload.admin_note
    )