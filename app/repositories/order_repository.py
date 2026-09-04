from sqlalchemy import select
from sqlalchemy import select, func, case
from sqlalchemy.orm import (
    joinedload
)
from sqlalchemy import func
from app.models.models import (
    Coupon,
    StoreSetting,
    Order,
    OrderItem,
    Product
)
from app.models.models import (
    Coupon,
    StoreSetting,
    Order,
    OrderItem,
    Product,
    User,
    OrderStatus
)
from sqlalchemy import select, func, or_

from app.models.models import (
    Order,
    User
)

class OrderRepository:

    @staticmethod
    async def get_coupon_by_code(
        db,
        code: str
    ):

        result = await db.execute(
            select(Coupon)
            .where(
                Coupon.code == code,
                Coupon.is_active == True
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_store_settings(
        db
    ):

        result = await db.execute(
            select(StoreSetting)
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def create_order(
        db,
        order: Order
    ):

        db.add(order)

        await db.flush()

        return order

    @staticmethod
    async def create_order_item(
        db,
        order_item: OrderItem
    ):

        db.add(order_item)

        await db.flush()

        return order_item

    @staticmethod
    async def get_order_by_id(
        db,
        order_id
    ):

        result = await db.execute(
            select(Order)
            .options(
                joinedload(Order.user),

                joinedload(Order.items)
                .joinedload(OrderItem.product),

                joinedload(Order.items)
                .joinedload(OrderItem.variant),

                joinedload(Order.address),

                joinedload(Order.payments),

                joinedload(Order.shipment)
            )
            .where(
                Order.id == order_id
            )
        )

        return (
            result
            .unique()
            .scalar_one_or_none()
        )

    @staticmethod
    async def get_orders_by_user(
        db,
        user_id
    ):

        result = await db.execute(
            select(Order)
            .options(
                joinedload(Order.user),

                joinedload(Order.items)
                .joinedload(OrderItem.product),

                joinedload(Order.items)
                .joinedload(OrderItem.variant),

                joinedload(Order.address),

                joinedload(Order.payments),

                joinedload(Order.shipment)
            )
            .where(
                Order.user_id == user_id
            )
            .order_by(
                Order.created_at.desc()
            )
        )

        return (
            result
            .unique()
            .scalars()
            .all()
        )

    @staticmethod
    async def get_order_details(
        db,
        order_id,
        user_id
    ):

        result = await db.execute(
            select(Order)
            .options(
                joinedload(Order.user),

                joinedload(Order.items)
                .joinedload(OrderItem.product),

                joinedload(Order.items)
                .joinedload(OrderItem.variant),

                joinedload(Order.address),

                joinedload(Order.payments),

                joinedload(Order.shipment)
            )
            .where(
                Order.id == order_id,
                Order.user_id == user_id
            )
        )

        return (
            result
            .unique()
            .scalar_one_or_none()
        )

    @staticmethod
    async def update_order(
        db,
        order
    ):

        await db.commit()

        await db.refresh(order)

        return order

    @staticmethod
    async def commit(
        db
    ):

        await db.commit()
    


    @staticmethod
    async def get_orders(
        db,
        page: int,
        page_size: int,
        search=None,
        status=None,
        payment_status=None
    ):

        query = (
            select(Order)
            .join(User)
            .options(
                joinedload(Order.user),

                joinedload(Order.address),

                joinedload(Order.items)
                .joinedload(OrderItem.product),

                joinedload(Order.items)
                .joinedload(OrderItem.variant),

                joinedload(Order.payments)
            )
        )

        if search:
            query = query.where(
                or_(
                    Order.order_number.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%"),
                    User.phone.ilike(f"%{search}%")
                )
            )

        if status:
            query = query.where(
                Order.status == status
            )

        if payment_status:
            query = query.where(
                Order.payment_status == payment_status
            )

        total_query = (
            select(func.count())
            .select_from(query.subquery())
        )

        total = await db.scalar(total_query)

        query = (
            query
            .order_by(Order.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await db.execute(query)

        orders = (
            result
            .unique()
            .scalars()
            .all()
        )

        return orders, total

    @staticmethod
    async def update_order_status(
        db,
        order_id,
        status
    ):

        order = await OrderRepository.get_order_by_id(
            db,
            order_id
        )

        if not order:
            return None

        order.status = status

        await db.commit()

        await db.refresh(order)

        return order
    

    @staticmethod
    async def update_payment_status(
        db,
        order_id,
        payment_status
    ):

        order = await OrderRepository.get_order_by_id(
            db,
            order_id
        )

        if not order:
            return None

        order.payment_status = payment_status

        await db.commit()

        await db.refresh(order)

        return order
    

    @staticmethod
    async def cancel_order(
        db,
        order_id,
        reason
    ):

        order = await OrderRepository.get_order_by_id(
            db,
            order_id
        )

        if not order:
            return None

        order.status = OrderStatus.CANCELLED

        order.cancel_reason = reason

        await db.commit()

        await db.refresh(order)

        return order
    

    
   

    @staticmethod
    async def get_order_summary(db):

        result = await db.execute(
            select(
                func.count(Order.id).label("total_orders"),

                func.coalesce(
                    func.sum(Order.total_amount),
                    0
                ).label("revenue"),

                func.sum(
                    case(
                        (Order.status == OrderStatus.PENDING, 1),
                        else_=0
                    )
                ).label("pending"),

                func.sum(
                    case(
                        (
                            Order.status.in_([
                                OrderStatus.SHIPPED,
                                OrderStatus.OUT_FOR_DELIVERY
                            ]),
                            1
                        ),
                        else_=0
                    )
                ).label("in_transit"),

                func.sum(
                    case(
                        (Order.status == OrderStatus.DELIVERED, 1),
                        else_=0
                    )
                ).label("delivered"),

                func.sum(
                    case(
                        (Order.status == OrderStatus.CANCELLED, 1),
                        else_=0
                    )
                ).label("cancelled")
            )
        )

        return result.mappings().one()
    

    
    