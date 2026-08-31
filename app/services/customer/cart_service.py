from uuid import UUID
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.models.models import CartItem
from app.repositories.cart_repository import CartRepository
from app.repositories.coupon_repository import CouponRepository
from app.repositories.setting_repository import SettingRepository
from app.repositories.product_repository import ProductRepository
from app.utils.pagination import build_pagination

class CartService:

        
        @staticmethod
        async def add_to_cart(
            db,
            user_id: UUID,
            product_id: UUID,
            quantity: int
        ):
            try:

                product = await ProductRepository.get_by_id(
                    db,
                    product_id
                )

                if not product:
                    raise HTTPException(
                        status_code=404,
                        detail="Product not found"
                    )

                if product.stock_qty <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail="Product is out of stock"
                    )

                if quantity <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail="Quantity must be greater than zero"
                    )

                if quantity > product.stock_qty:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Only {product.stock_qty} item(s) available in stock"
                    )

                existing = await CartRepository.get_by_user_and_product(
                    db,
                    user_id,
                    product_id
                )

                if existing:

                    existing.quantity = quantity

                    await CartRepository.update(
                        db,
                        existing
                    )

                    return {
                        "success": True,
                        "status_code": 200,
                        "message": "Cart quantity updated successfully",
                        "data": {
                            "product_id": str(product.id),
                            "quantity": existing.quantity
                        }
                    }

                cart_item = CartItem(
                    user_id=user_id,
                    product_id=product_id,
                    quantity=quantity
                )

                await CartRepository.create(
                    db,
                    cart_item
                )

                return {
                    "success": True,
                    "status_code": 201,
                    "message": "Product added to cart",
                    "data": {
                        "product_id": str(product.id),
                        "quantity": quantity
                    }
                }

            except HTTPException:
                raise

            except SQLAlchemyError:
                raise HTTPException(
                    status_code=500,
                    detail="Database error while adding product to cart"
                )

            except Exception:
                raise HTTPException(
                    status_code=500,
                    detail="Something went wrong"
                )
        @staticmethod
        async def get_cart(
            db,
            user_id: UUID,
            page: int,
            page_size: int
        ):

            items, total_records = (
                await CartRepository.get_cart_items(
                    db=db,
                    user_id=user_id,
                    page=page,
                    page_size=page_size
                )
            )

            if not items:

                return {
                    "success": True,
                    "status_code": 200,
                    "message": "Cart is empty",
                    "data": [],
                    "pagination": {
                        "current_page": page,
                        "page_size": page_size,
                        "total_records": 0,
                        "total_pages": 0,
                        "has_next": False,
                        "has_previous": False
                    }
                }

            response_data = []

            subtotal = 0

            for item in items:

                product = item.product

                item_total = (
                    float(product.sale_price)
                    * item.quantity
                )

                subtotal += item_total

                response_data.append(
                    {
                        "cart_id": str(item.id),

                        "product_id": str(product.id),

                        "category_id": str(product.category_id)
                        if product.category_id
                        else None,

                        "category_name": (
                            product.category.name
                            if product.category
                            else None
                        ),

                        "name": product.name,
                        "slug": product.slug,
                        "sku": product.sku,
                        "brand": product.brand,

                        "mrp": float(product.mrp),
                        "sale_price": float(product.sale_price),

                        "quantity": item.quantity,

                        "item_total": item_total,

                        "stock_qty": product.stock_qty,

                        "thumbnail_url": product.thumbnail_url,

                        "images": [
                            {
                                "id": str(img.id),
                                "image_url": img.image_url,
                                "is_primary": img.is_primary,
                                "sort_order": img.sort_order
                            }
                            for img in product.images
                        ]
                    }
                )

            return {
                "success": True,
                "status_code": 200,
                "message": "Cart fetched successfully",
                "data": response_data,
                "cart_summary": {
                    "subtotal": subtotal,
                    "total_items": len(items)
                },
                "pagination": build_pagination(
                    page=page,
                    page_size=page_size,
                    total_records=total_records
                )
            }

        @staticmethod
        async def remove_from_cart(
            db,
            user_id: UUID,
            product_id: UUID
        ):
            try:

                item = await CartRepository.get_by_user_and_product(
                    db,
                    user_id,
                    product_id
                )

                if not item:
                    raise HTTPException(
                        status_code=404,
                        detail="Product not found in cart"
                    )

                await CartRepository.delete(
                    db,
                    item
                )

                return {
                    "success": True,
                    "status_code": 200,
                    "message": "Product removed from cart"
                }

            except HTTPException:
                raise

            except SQLAlchemyError:
                raise HTTPException(
                    status_code=500,
                    detail="Database error while removing product from cart"
                )

            except Exception:
                raise HTTPException(
                    status_code=500,
                    detail="Something went wrong"
                )





        @staticmethod
        async def get_cart_summary(
            db,
            user_id
        ):

            cart_items = (
                await CartRepository.get_all_cart_items(
                    db=db,
                    user_id=user_id
                )
            )

            if not cart_items:

                return {
                    "success": True,
                    "status_code": 200,
                    "message": "Cart is empty",
                    "data": {
                        "subtotal": 0,
                        "shipping_charge": 0,
                        "total_amount": 0,
                        "available_coupons": []
                    }
                }

            subtotal = Decimal("0")

            total_quantity = 0

            for item in cart_items:

                item_total = (
                    Decimal(str(item.product.sale_price))
                    * item.quantity
                )

                subtotal += item_total

                total_quantity += item.quantity

            # ------------------------
            # DELIVERY CHARGE
            # ------------------------

            shipping_charge = Decimal("0")

            settings = await SettingRepository.get_settings(
                db
            )

            if settings:

                delivery_charge = Decimal(
                    str(
                        settings.delivery_charge or 0
                    )
                )

                free_shipping_threshold = Decimal(
                    str(
                        settings.free_shipping_threshold or 0
                    )
                )

                if delivery_charge > 0:

                    if (
                        free_shipping_threshold > 0
                        and
                        subtotal >= free_shipping_threshold
                    ):
                        shipping_charge = Decimal("0")

                    else:
                        shipping_charge = delivery_charge

            total_amount = (
                subtotal +
                shipping_charge
            )

            # ------------------------
            # COUPONS
            # ------------------------

            coupons = await CouponRepository.get_active_coupons(
                db
            )

            coupon_list = []

            for coupon in coupons:

                is_applicable = True

                reason = None

                discount_amount = Decimal("0")

                if (
                    subtotal <
                    coupon.minimum_order_amount
                ):
                    is_applicable = False

                    reason = (
                        f"Minimum order amount "
                        f"{coupon.minimum_order_amount}"
                    )

                if (
                    coupon.usage_limit
                    and
                    coupon.used_count >=
                    coupon.usage_limit
                ):
                    is_applicable = False

                    reason = (
                        "Coupon usage limit reached"
                    )

                if is_applicable:

                    if (
                        coupon.coupon_type.value
                        == "percentage"
                    ):

                        discount_amount = (
                            subtotal *
                            coupon.discount_value
                        ) / Decimal("100")

                        if (
                            coupon.max_discount_amount
                            and
                            discount_amount >
                            coupon.max_discount_amount
                        ):
                            discount_amount = (
                                coupon.max_discount_amount
                            )

                    elif (
                        coupon.coupon_type.value
                        == "flat"
                    ):

                        discount_amount = (
                            coupon.discount_value
                        )

                    elif (
                        coupon.coupon_type.value
                        == "free_shipping"
                    ):

                        discount_amount = (
                            shipping_charge
                        )

                coupon_list.append(
                    {
                        "coupon_id": str(coupon.id),
                        "coupon_code": coupon.code,
                        "coupon_title": coupon.title,
                        "is_applicable": is_applicable,
                        "reason": reason,
                        "discount_amount": float(
                            discount_amount
                        ),
                        "payable_amount": float(
                            max(
                                Decimal("0"),
                                total_amount -
                                discount_amount
                            )
                        )
                    }
                )

            return {
                "success": True,
                "status_code": 200,
                "message": "Order summary fetched successfully",
                "data": {
                    "total_items": total_quantity,
                    "subtotal": float(subtotal),
                    "shipping_charge": float(
                        shipping_charge
                    ),
                    "total_amount": float(
                        total_amount
                    ),
                    "available_coupons": coupon_list
                }
            }


        @staticmethod
        async def apply_coupon(
            db,
            user_id,
            coupon_code
        ):
            try:

                summary = await CartService.get_cart_summary(
                    db=db,
                    user_id=user_id
                )

                coupons = summary["data"]["available_coupons"]

                selected_coupon = next(
                    (
                        coupon
                        for coupon in coupons
                        if coupon["coupon_code"] == coupon_code
                    ),
                    None
                )

                if not selected_coupon:
                    raise HTTPException(
                        status_code=404,
                        detail="Coupon not found"
                    )

                if not selected_coupon["is_applicable"]:
                    raise HTTPException(
                        status_code=400,
                        detail=selected_coupon["reason"]
                    )

                return {
                    "success": True,
                    "status_code": 200,
                    "message": "Coupon applied successfully",
                    "data": {
                        "coupon_id": selected_coupon["coupon_id"],
                        "coupon_code": selected_coupon["coupon_code"],
                        "discount_amount": selected_coupon["discount_amount"],
                        "payable_amount": selected_coupon["payable_amount"]
                    }
                }

            except HTTPException:
                raise

            except SQLAlchemyError:
                raise HTTPException(
                    status_code=500,
                    detail="Database error while applying coupon"
                )

            except Exception:
                raise HTTPException(
                    status_code=500,
                    detail="Something went wrong"
                )