from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:

    @staticmethod
    async def get_dashboard(db):

        return {
            "summary":
                await DashboardRepository.get_summary(db),

            "revenue_trend":
                await DashboardRepository.get_revenue_trend(db),

            "orders_by_category":
                await DashboardRepository.get_orders_by_category(db),

            "peak_shopping_hours":
                await DashboardRepository.get_peak_shopping_hours(db),

            "top_selling_products":
                await DashboardRepository.get_top_selling_products(db),

            "recent_orders":
                await DashboardRepository.get_recent_orders(db),

            "abandoned_carts":
                await DashboardRepository.get_abandoned_carts(db)
        }