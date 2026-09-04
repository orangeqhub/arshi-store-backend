import uuid

from decimal import Decimal

from app.models.models import (
    Order,
    OrderItem,
    CouponUsage,
    Payment,
    OrderStatus,
    PaymentStatus
)

from app.repositories.cart_repository import (
    CartRepository
)

from app.repositories.order_repository import (
    OrderRepository
)

from app.repositories.coupon_repository import (
    CouponRepository
)

from app.repositories.setting_repository import (
    SettingRepository
)

from app.services.shipping.bluedart_service import (
    BlueDartService
)


import uuid

from decimal import Decimal

from app.models.models import (
    Order,
    OrderItem,
    Payment,
    OrderStatus,
    PaymentStatus
)


def _cart_line_price(item):
    """Server-side authoritative unit price for a cart line — variant price
    when a variant is selected, product price otherwise. Never derived from
    client input."""

    return (
        item.variant.sale_price
        if item.variant
        else item.product.sale_price
    )


class OrderService:
        @staticmethod
        async def create_order(
            db,
            user_id,
            payload
        ):

            cart_items = await (
                CartRepository.get_all_cart_items(
                    db,
                    user_id
                )
            )

            if not cart_items:

                return {
                    "success": False,
                    "status_code": 400,
                    "message": "Cart is empty"
                }

            subtotal = Decimal("0")

            for item in cart_items:

                subtotal += (
                    _cart_line_price(item) *
                    item.quantity
                )

            settings = await (
                SettingRepository.get_settings(
                    db
                )
            )

            shipping_charge = Decimal("0")

            if (
                settings and
                subtotal <
                settings.free_shipping_threshold
            ):
                shipping_charge = (
                    settings.delivery_charge
                )

            discount = Decimal("0")
            coupon = None

            if payload.coupon_code:

                coupon = await (
                    CouponRepository.get_coupon_by_code(
                        db,
                        payload.coupon_code
                    )
                )

                if coupon:

                    if (
                        coupon.coupon_type.value ==
                        "flat"
                    ):

                        discount = (
                            coupon.discount_value
                        )

                    elif (
                        coupon.coupon_type.value ==
                        "percentage"
                    ):

                        discount = (
                            subtotal *
                            coupon.discount_value
                        ) / Decimal("100")

            total_amount = (
                subtotal +
                shipping_charge -
                discount
            )

            order = Order(
                order_number=
                f"SW-{uuid.uuid4().hex[:10].upper()}",
                user_id=user_id,
                address_id=payload.address_id,
                coupon_id=(
                    coupon.id
                    if coupon
                    else None
                ),
                coupon_code=(
                    coupon.code
                    if coupon
                    else None
                ),
                subtotal=subtotal,
                gst_amount=Decimal("0"),
                shipping_charge=shipping_charge,
                discount=discount,
                total_amount=total_amount,
                status=OrderStatus.PENDING,
                payment_status=
                PaymentStatus.PENDING
            )

            await (
                OrderRepository.create_order(
                    db,
                    order
                )
            )

            for item in cart_items:

                unit_price = _cart_line_price(item)

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product.id,
                    variant_id=item.variant.id if item.variant else None,
                    product_name=item.product.name,
                    product_sku=item.product.sku,
                    variant_label=item.variant.label if item.variant else None,
                    variant_sku=item.variant.sku if item.variant else None,
                    quantity=item.quantity,
                    price=unit_price,
                    gst_amount=Decimal("0"),
                    total=(
                        unit_price *
                        item.quantity
                    )
                )

                await (
                    OrderRepository.create_order_item(
                        db,
                        order_item
                    )
                )

            payment = Payment(
                order_id=order.id,
                payment_method=
                payload.payment_method,
                amount=total_amount,
                status=
                PaymentStatus.PENDING
            )

            db.add(payment)

            await db.commit()

            return {
                "success": True,
                "status_code": 201,
                "message":
                "Order created. Complete payment.",
                "data": {
                    "order_id":
                    str(order.id),
                    "order_number":
                    order.order_number,
                    "amount":
                    float(total_amount)
                }
            }

        @staticmethod
        async def payment_success(
            db,
            user_id,
            payload
        ):

            order = await (
                OrderRepository.get_order_by_id(
                    db,
                    payload.order_id
                )
            )

            if not order:

                return {
                    "success": False,
                    "status_code": 404,
                    "message": "Order not found"
                }

            if order.payment_status == PaymentStatus.PAID:

                return {
                    "success": False,
                    "status_code": 400,
                    "message": "Payment already completed"
                }

            payment = order.payments[0]

            payment.status = (
                PaymentStatus.PAID
            )

            payment.gateway_transaction_id = (
                payload.transaction_id
            )

            order.payment_status = (
                PaymentStatus.PAID
            )

            order.status = (
                OrderStatus.CONFIRMED
            )

            # Reduce stock (variant stock takes precedence when the line has one)
            for item in order.items:

                product = item.product
                variant = item.variant

                stock_holder = variant if variant else product

                if stock_holder.stock_qty < item.quantity:

                    return {
                        "success": False,
                        "status_code": 400,
                        "message": (
                            f"{product.name} stock unavailable"
                        )
                    }

                stock_holder.stock_qty -= item.quantity

            # Coupon usage
            if order.coupon_id:

                coupon_usage = CouponUsage(
                    coupon_id=order.coupon_id,
                    user_id=user_id,
                    order_id=order.id,
                    discount_amount=order.discount
                )

                db.add(coupon_usage)

                if order.coupon:
                    order.coupon.used_count += 1

            # Clear cart
            cart_items = await (
                CartRepository.get_all_cart_items(
                    db,
                    user_id
                )
            )

            for item in cart_items:

                await db.delete(item)

            await db.commit()

            return {
                "success": True,
                "status_code": 200,
                "message":
                "Payment successful. Order confirmed."
            }
        @staticmethod
        async def get_orders(
            db,
            user_id
        ):

            orders = await (
                OrderRepository.get_orders_by_user(
                    db,
                    user_id
                )
            )

            return {
                "success": True,
                "status_code": 200,
                "data": [
    {
        "order_id": str(order.id),

        "order_number": order.order_number,

        "status": order.status.value,

        "payment_status": order.payment_status.value,

        "total_amount": float(
            order.total_amount
        ),

        "products": [
                            {
                                "product_id": str(
                                    item.product_id
                                ),

                                "product_name":
                                    item.product_name,

                                "product_image":
                                    item.product.thumbnail_url
                                    if item.product
                                    else None
                            }
                            for item in order.items
                        ],

        "shipment": (
            {
                "courier_name": order.shipment.courier_name,
                "awb_number": order.shipment.awb_number,
                "status": order.shipment.status,
            }
            if order.shipment else None
        )
                    }
                    for order in orders
                ]
            }

        @staticmethod
        async def get_order(
            db,
            user_id,
            order_id
        ):

            order = await (
                OrderRepository.get_order_details(
                    db,
                    order_id,
                    user_id
                )
            )

            if not order:

                return {
                    "success": False,
                    "status_code": 404,
                    "message":
                    "Order not found"
                }

            return {
                "success": True,
                "status_code": 200,
                "data": {
                    "order_id":
                    str(order.id),

                    "order_number":
                    order.order_number,

                    "status":
                    order.status.value,

                    "payment_status":
                    order.payment_status.value,

                    "subtotal":
                    float(order.subtotal),

                    "shipping_charge":
                    float(
                        order.shipping_charge
                    ),

                    "discount":
                    float(order.discount),

                    "total_amount":
                    float(
                        order.total_amount
                    ),

                    "items": [
                                {
                                    "product_id": str(
                                        item.product_id
                                    ),

                                    "product_name":
                                        item.product_name,

                                    "product_sku":
                                        item.product_sku,

                                    "variant_label":
                                        item.variant_label,

                                    "variant_sku":
                                        item.variant_sku,

                                    "product_image":
                                        item.product.thumbnail_url
                                        if item.product
                                        else None,

                                    "quantity":
                                        item.quantity,

                                    "price":
                                        float(item.price),

                                    "total":
                                        float(item.total)
                                }
                                for item in order.items
                            ],

                    "shipment": (
                        {
                            "courier_name": order.shipment.courier_name,
                            "awb_number": order.shipment.awb_number,
                            "status": order.shipment.status,
                            "shipped_at": order.shipment.shipped_at,
                            "estimated_delivery":
                                order.shipment.estimated_delivery,
                        }
                        if order.shipment else None
                    )
                }
            }

        @staticmethod
        async def track_shipment(
            db,
            user_id,
            order_id
        ):

            order = await (
                OrderRepository.get_order_details(
                    db,
                    order_id,
                    user_id
                )
            )

            if not order:

                return {
                    "success": False,
                    "status_code": 404,
                    "message":
                    "Order not found"
                }

            if not order.shipment or not order.shipment.awb_number:

                return {
                    "success": False,
                    "status_code": 404,
                    "message":
                    "Shipment not yet created for this order"
                }

            shipment = await (
                BlueDartService.refresh_tracking(
                    db,
                    order.shipment
                )
            )

            return {
                "success": True,
                "status_code": 200,
                "data": {
                    "courier_name": shipment.courier_name,
                    "awb_number": shipment.awb_number,
                    "status": shipment.status,
                    "shipped_at": shipment.shipped_at,
                    "estimated_delivery":
                        shipment.estimated_delivery,
                }
            }

        @staticmethod
        async def cancel_order(
            db,
            user_id,
            order_id,
            reason
        ):

            order = await (
                OrderRepository.get_order_details(
                    db,
                    order_id,
                    user_id
                )
            )

            if not order:

                return {
                    "success": False,
                    "status_code": 404,
                    "message":
                    "Order not found"
                }

            if order.status in [
                OrderStatus.SHIPPED,
                OrderStatus.OUT_FOR_DELIVERY,
                OrderStatus.DELIVERED
            ]:

                return {
                    "success": False,
                    "status_code": 400,
                    "message":
                    "Order cannot be cancelled"
                }

            order.status = (
                OrderStatus.CANCELLED
            )

            order.cancel_reason = reason

            await db.commit()

            return {
                "success": True,
                "status_code": 200,
                "message":
                "Order cancelled successfully"
            }   
        



        @staticmethod
        async def create_payment_order(
            db,
            user_id,
            payload
        ):
            cart_items = await CartRepository.get_all_cart_items(
                db,
                user_id
            )

            if not cart_items:
                return {
                    "success": False,
                    "message": "Cart is empty"
                }

            subtotal = Decimal("0")

            for item in cart_items:
                subtotal += (
                    _cart_line_price(item) *
                    item.quantity
                )

            shipping_charge = Decimal("0")

            settings = await SettingRepository.get_settings(
                db
            )

            if (
                settings and
                subtotal < settings.free_shipping_threshold
            ):
                shipping_charge = settings.delivery_charge

            discount = Decimal("0")
            coupon = None

            if payload.coupon_code:

                coupon = await CouponRepository.get_by_code(
                    db,
                    payload.coupon_code
                )

                if coupon:

                    if coupon.coupon_type.value == "flat":

                        discount = coupon.discount_value

                    elif coupon.coupon_type.value == "percentage":

                        discount = (
                            subtotal *
                            coupon.discount_value
                        ) / Decimal("100")

            total_amount = (
                subtotal +
                shipping_charge -
                discount
            )

            return {
                "success": True,
                "amount": float(total_amount),
                "coupon_code": payload.coupon_code,
                "address_id": str(payload.address_id)
            }
        


        

        @staticmethod
        async def clear_cart(
            db,
            user_id
        ):
            items = await CartRepository.get_all_cart_items(
                db,
                user_id
            )

            for item in items:
                await db.delete(item)

            await db.flush()