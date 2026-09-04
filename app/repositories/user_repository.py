from sqlalchemy import select

from app.models.models import User

from sqlalchemy import (
    select,
    func,
    desc
)

from sqlalchemy.orm import (
    joinedload
)

from app.models.models import (
    User,
    Order,
    Address,
    WishlistItem
)


class UserRepository:

    async def get_by_email(
        self,
        db,
        email: str
    ):

        result = await db.execute(
            select(User).where(
                User.email == email
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        db,
        user
    ):

        db.add(user)

        await db.commit()

        await db.refresh(user)

        return user
    



    @staticmethod
    async def get_customers(
        db,
        page: int,
        page_size: int,
        search=None
    ):

        query = (
            select(User)
            .where(User.role == "customer")
        )

        if search:
            query = query.where(
                User.full_name.ilike(f"%{search}%")
            )

        total = await db.scalar(
            select(func.count())
            .select_from(query.subquery())
        )

        result = await db.execute(
            query
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        customers = result.scalars().all()

        return customers, total


    @staticmethod
    async def get_customer_details(
        db,
        customer_id
    ):

        result = await db.execute(
            select(User)
            .options(
                joinedload(User.orders),
                joinedload(User.addresses),
                joinedload(User.wishlist_items)
            )
            .where(
                User.id == customer_id
            )
        )

        return (
            result
            .unique()
            .scalar_one_or_none()
        )