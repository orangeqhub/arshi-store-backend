from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.models.models import (
    Review,
    ReviewStatus,
    Order,
    OrderItem,
    OrderStatus
)


class ReviewRepository:

    @staticmethod
    async def has_purchased_product(
        db,
        user_id: UUID,
        product_id: UUID
    ):

        result = await db.execute(
            select(OrderItem.id)
            .join(
                Order,
                OrderItem.order_id == Order.id
            )
            .where(
                Order.user_id == user_id,
                OrderItem.product_id == product_id,
                Order.status == OrderStatus.DELIVERED
            )
            .limit(1)
        )

        return result.scalar()

    @staticmethod
    async def create(
        db,
        review: Review
    ):

        db.add(review)

        await db.commit()
        await db.refresh(review)

        return review

    @staticmethod
    async def get_review_by_id(
        db,
        review_id
    ):

        result = await db.execute(
            select(Review)
            .where(
                Review.id == review_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_reviews(
        db,
        status: str | None = None
    ):

        query = (
            select(Review)
            .options(
                joinedload(Review.user),
                joinedload(Review.product)
            )
            .order_by(
                Review.created_at.desc()
            )
        )

        if status:
            query = query.where(
                Review.status == status
            )

        result = await db.execute(query)

        return result.unique().scalars().all()

    @staticmethod
    async def get_by_id(
        db,
        review_id
    ):

        result = await db.execute(
            select(Review)
            .options(
                joinedload(Review.user),
                joinedload(Review.product)
            )
            .where(
                Review.id == review_id
            )
        )

        return result.unique().scalar_one_or_none()

    @staticmethod
    async def save(
        db,
        review
    ):

        await db.commit()
        await db.refresh(review)

        return review

    @staticmethod
    async def get_dashboard_stats(
        db
    ):

        total_reviews = await db.scalar(
            select(func.count(Review.id))
        )

        pending_reviews = await db.scalar(
            select(func.count(Review.id))
            .where(
                Review.status == ReviewStatus.PENDING
            )
        )

        flagged_reviews = await db.scalar(
            select(func.count(Review.id))
            .where(
                Review.status == ReviewStatus.FLAGGED
            )
        )

        average_rating = await db.scalar(
            select(func.avg(Review.rating))
        )

        return {
            "average_rating": round(float(average_rating or 0), 1),
            "total_reviews": total_reviews,
            "pending_reviews": pending_reviews,
            "flagged_reviews": flagged_reviews
        }