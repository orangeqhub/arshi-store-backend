from datetime import datetime, timedelta

from sqlalchemy import func, distinct, extract, desc
from sqlalchemy.future import select

from app.models.models import (
    User,
    Order,
    OrderItem,
    Product,
    Category,
    CartItem,
    OrderStatus
)


class DashboardRepository:

    @staticmethod
    async def get_summary(db):

        today = datetime.utcnow().date()

        revenue = await db.scalar(
            select(func.coalesce(func.sum(Order.total_amount), 0))
            .where(Order.status == OrderStatus.DELIVERED)
        )

        orders_today = await db.scalar(
            select(func.count(Order.id))
            .where(func.date(Order.created_at) == today)
        )

        pending_deliveries = await db.scalar(
            select(func.count(Order.id))
            .where(
                Order.status.in_([
                    OrderStatus.CONFIRMED,
                    OrderStatus.PACKED,
                    OrderStatus.SHIPPED,
                    OrderStatus.OUT_FOR_DELIVERY
                ])
            )
        )

        total_customers = await db.scalar(
            select(func.count(User.id))
            .where(User.role == "customer")
        )

        total_orders = await db.scalar(
            select(func.count(Order.id))
        )

        unique_buyers = await db.scalar(
            select(func.count(distinct(Order.user_id)))
        )

        conversion_rate = (
            (unique_buyers / total_customers) * 100
            if total_customers else 0
        )

        repeat_customers = await db.scalar(
            select(func.count())
            .select_from(
                select(Order.user_id)
                .group_by(Order.user_id)
                .having(func.count(Order.id) > 1)
                .subquery()
            )
        )

        returning_percentage = (
            (repeat_customers / total_customers) * 100
            if total_customers else 0
        )

        return {
            "total_revenue": float(revenue),
            "orders_today": orders_today,
            "pending_deliveries": pending_deliveries,
            "total_customers": total_customers,
            "conversion_rate": round(conversion_rate, 2),
            "returning_customers_percentage": round(returning_percentage, 2)
        }
    
    @staticmethod
    async def get_revenue_trend(db):

            last_14_days = datetime.utcnow() - timedelta(days=14)

            result = await db.execute(
                select(
                    func.date(Order.created_at),
                    func.sum(Order.total_amount)
                )
                .where(Order.created_at >= last_14_days)
                .group_by(func.date(Order.created_at))
                .order_by(func.date(Order.created_at))
            )

            return [
                {
                    "date": str(row[0]),
                    "revenue": float(row[1] or 0)
                }
                for row in result.all()
            ]
    @staticmethod
    async def get_orders_by_category(db):

            result = await db.execute(
                select(
                    Category.name,
                    func.sum(OrderItem.quantity)
                )
                .join(Product, Product.category_id == Category.id)
                .join(OrderItem, OrderItem.product_id == Product.id)
                .group_by(Category.name)
            )

            rows = result.all()

            total = sum(row[1] for row in rows)

            return [
                {
                    "category_name": row[0],
                    "total_orders": row[1],
                    "percentage": round((row[1] / total) * 100, 2)
                }
                for row in rows
            ]
    

    @staticmethod
    async def get_peak_shopping_hours(db):

            result = await db.execute(
                select(
                    extract("hour", Order.created_at),
                    func.count(Order.id)
                )
                .group_by(
                    extract("hour", Order.created_at)
                )
                .order_by(
                    extract("hour", Order.created_at)
                )
            )

            return [
                {
                    "hour": f"{int(row[0]):02d}:00",
                    "orders_count": row[1]
                }
                for row in result.all()
            ]
    

    @staticmethod
    async def get_top_selling_products(db):

        result = await db.execute(
            select(
                Product.id,
                Product.name,
                func.sum(OrderItem.quantity),
                func.sum(OrderItem.total)
            )
            .join(OrderItem)
            .group_by(
                Product.id,
                Product.name
            )
            .order_by(
                desc(func.sum(OrderItem.quantity))
            )
            .limit(5)
        )

        return [
            {
                "product_id": str(row[0]),
                "product_name": row[1],
                "total_sold": row[2],
                "revenue": float(row[3])
            }
            for row in result.all()
        ]
    


    @staticmethod
    async def get_recent_orders(db):

        result = await db.execute(
            select(
                Order.order_number,
                User.full_name,
                Order.total_amount,
                Order.status
            )
            .join(User)
            .order_by(Order.created_at.desc())
            .limit(10)
        )

        return [
            {
                "order_number": row[0],
                "customer_name": row[1],
                "amount": float(row[2]),
                "status": row[3].value
            }
            for row in result.all()
        ]
    


    @staticmethod
    async def get_abandoned_carts(db):

        result = await db.execute(
            select(
                User.full_name,
                func.count(CartItem.id),
                func.sum(
                    CartItem.quantity *
                    Product.sale_price
                )
            )
            .join(CartItem)
            .join(Product)
            .group_by(User.full_name)
            .limit(5)
        )

        return [
            {
                "customer_name": row[0],
                "items_count": row[1],
                "cart_value": float(row[2] or 0)
            }
            for row in result.all()
        ]