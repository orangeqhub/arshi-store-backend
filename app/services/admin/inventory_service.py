from app.repositories.inventory_repository import (
    InventoryRepository
)


class InventoryService:

    @staticmethod
    async def get_inventory_dashboard(db):

        (
            total_stock,
            low_stock,
            out_of_stock,
            movements_today,
            products
        ) = await InventoryRepository.get_inventory_dashboard(
            db
        )

        inventory_products = []

        for product in products:

            if product.stock_qty == 0:
                status = "out_of_stock"

            elif product.stock_qty <= 25:
                status = "low"

            else:
                status = "healthy"

            inventory_products.append({
                "product_id": str(product.id),
                "product_name": product.name,
                "sku": product.sku,
                "stock_qty": product.stock_qty,
                "status": status,
                "stock_percentage": min(
                    product.stock_qty,
                    100
                )
            })

        return {
            "summary": {
                "units_in_stock": total_stock,
                "low_stock": low_stock,
                "out_of_stock": out_of_stock,
                "stock_movements_today": movements_today
            },
            "products": inventory_products
        }