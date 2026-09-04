from fastapi import APIRouter

# Auth
from app.api.routes.auth.auth_routes import router as auth_router

# Admin
from app.api.routes.admin.category_routes import router as admin_category_router
from app.api.routes.admin.product_routes import router as admin_product_router
from app.api.routes.admin.category_icon_routes import router as category_icon_routes
from app.api.routes.admin.coupon_routes import router as coupon_routes
from app.api.routes.store.product_routes import router as store_product_router
from app.api.routes.store.category_routes import router as store_category_router
from app.api.routes.customer.address_routes import router as address_router
from app.api.routes.customer.wishlist_routes import router as wishlist_router
from app.api.routes.customer.cart_routes import router as cart_router
from app.api.routes.customer.order_routes import router as customer_order_router
from app.api.routes.admin.dashboard_routes import router as dashboard_router
from app.api.routes.admin.order_routes import router as admin_order_router
from app.api.routes.admin.inventory_routes import router as inventory_router
from app.api.routes.admin.user_routes import router as user_router
from app.api.routes.admin.setting_routes import router as setting_router
from app.api.routes.customer.review_routes import router as review_router
from app.api.routes.admin.review_routes import router as admin_review_router
from app.api.routes.admin.cms_routes import router as admin_cms_router
from app.api.routes.shop.billing_routes import (router as billing_router)
from app.api.routes.store.cms_routes import router as store_cms_router
from app.api.routes.admin.shipping_routes import router as admin_shipping_router
from app.api.routes.admin.shipping_routes import diagnostics_router as admin_shipping_diagnostics_router
'''from app.api.routes.admin.dashboard_routes import router as dashboard_router
from app.api.routes.admin.inventory_routes import router as inventory_router
from app.api.routes.admin.order_routes import router as admin_order_router
from app.api.routes.admin.payment_routes import router as payment_router
from app.api.routes.admin.setting_routes import router as setting_router
from app.api.routes.admin.ticket_routes import router as ticket_router
from app.api.routes.admin.user_routes import router as user_router

# Store
from app.api.routes.store.category_routes import router as store_category_router
from app.api.routes.store.product_routes import router as store_product_router

# Customer
from app.api.routes.customer.profile_routes import router as profile_router
from app.api.routes.customer.cart_routes import router as cart_router
from app.api.routes.customer.order_routes import router as customer_order_router
from app.api.routes.customer.address_routes import router as address_router
from app.api.routes.customer.wishlist_routes import router as wishlist_router
from app.api.routes.customer.review_routes import router as review_router
'''

api_router = APIRouter()


# ==========================
# AUTH
# ==========================

api_router.include_router(auth_router)


# ==========================
# ADMIN
# ==========================
api_router.include_router(dashboard_router)
api_router.include_router(admin_category_router)
api_router.include_router(admin_product_router)
api_router.include_router(inventory_router)
api_router.include_router(admin_order_router)
api_router.include_router(user_router)
api_router.include_router(setting_router)
api_router.include_router(admin_review_router)

api_router.include_router(store_product_router)
api_router.include_router(store_category_router)
api_router.include_router(address_router)
api_router.include_router(wishlist_router)
api_router.include_router(cart_router)
api_router.include_router(coupon_routes)
api_router.include_router(category_icon_routes)
api_router.include_router(customer_order_router)
api_router.include_router(review_router)
api_router.include_router(billing_router)
api_router.include_router(admin_cms_router)
api_router.include_router(store_cms_router)
api_router.include_router(admin_shipping_router)
api_router.include_router(admin_shipping_diagnostics_router)
'''
api_router.include_router(inventory_router)

api_router.include_router(admin_order_router)

api_router.include_router(payment_router)

api_router.include_router(setting_router)

api_router.include_router(ticket_router)

api_router.include_router(user_router)


# ==========================
# STORE
# ==========================

api_router.include_router(store_category_router)

api_router.include_router(store_product_router)


# ==========================
# CUSTOMER
# ==========================

api_router.include_router(profile_router)

api_router.include_router(cart_router)

api_router.include_router(customer_order_router)

api_router.include_router(address_router)

api_router.include_router(wishlist_router)

api_router.include_router(review_router)'''