from uuid import UUID

from fastapi import HTTPException

from app.models.models import (
    Review,
    ReviewStatus
)

from app.repositories.review_repository import (
    ReviewRepository
)


class ReviewService:

    @staticmethod
    async def create_review(
        db,
        user_id,
        payload
    ):

        user_id = UUID(user_id)

        purchased_product = await ReviewRepository.has_purchased_product(
            db=db,
            user_id=user_id,
            product_id=payload.product_id
        )

        if not purchased_product:
            raise HTTPException(
                status_code=400,
                detail="You can review only delivered products that you purchased"
            )

        review = Review(
            product_id=payload.product_id,
            user_id=user_id,
            rating=payload.rating,
            review_text=payload.review_text,
            image_url=payload.image_url,
            is_verified_purchase=True,
            status=ReviewStatus.PENDING
        )

        review = await ReviewRepository.create(
            db=db,
            review=review
        )

        return {
            "success": True,
            "status_code": 201,
            "message": "Review submitted successfully and waiting for admin approval",
            "data": {
                "review_id": str(review.id),
                "status": review.status.value
            }
        }