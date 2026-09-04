from pydantic import BaseModel
from typing import List


class DashboardSummary(BaseModel):
    total_revenue: float
    orders_today: int
    pending_deliveries: int
    total_customers: int
    conversion_rate: float
    returning_customers_percentage: float


class RevenueTrend(BaseModel):
    date: str
    revenue: float


class CategoryAnalytics(BaseModel):
    category_name: str
    total_orders: int
    percentage: float


class PeakHourAnalytics(BaseModel):
    hour: str
    orders_count: int


class TopSellingProduct(BaseModel):
    product_id: str
    product_name: str
    total_sold: int
    revenue: float


class RecentOrder(BaseModel):
    order_number: str
    customer_name: str
    amount: float
    status: str


class AbandonedCart(BaseModel):
    customer_name: str
    cart_value: float
    items_count: int


class DashboardResponse(BaseModel):
    summary: DashboardSummary
    revenue_trend: List[RevenueTrend]
    orders_by_category: List[CategoryAnalytics]
    peak_shopping_hours: List[PeakHourAnalytics]
    top_selling_products: List[TopSellingProduct]
    recent_orders: List[RecentOrder]
    abandoned_carts: List[AbandonedCart]