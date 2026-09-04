from sqlalchemy import (
    select,
    func
)

from app.models.models import (
    Product,
    InventoryLog
)

from sqlalchemy.orm import joinedload


class InventoryRepository:

    @staticmethod
    async def get_inventory_dashboard(db):

        total_stock = await db.scalar(
            select(
                func.coalesce(
                    func.sum(Product.stock_qty),
                    0
                )
            )
            .where(
                Product.is_deleted == False
            )
        )

        low_stock = await db.scalar(
            select(func.count(Product.id))
            .where(
                Product.stock_qty.between(1, 25),
                Product.is_deleted == False
            )
        )

        out_of_stock = await db.scalar(
            select(func.count(Product.id))
            .where(
                Product.stock_qty == 0,
                Product.is_deleted == False
            )
        )

        movements_today = await db.scalar(
            select(
                func.count(
                    InventoryLog.id
                )
            )
        )

        result = await db.execute(
            select(Product)
            .options(
                joinedload(Product.category)
            )
            .where(
                Product.is_deleted == False
            )
            .order_by(
                Product.stock_qty.asc()
            )
        )

        products = (
            result
            .scalars()
            .all()
        )

        return (
            total_stock,
            low_stock,
            out_of_stock,
            movements_today,
            products
        )