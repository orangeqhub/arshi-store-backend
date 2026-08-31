from app.repositories.order_repository import (
    OrderRepository
)


class OrderService:

    @staticmethod
    async def get_orders(
        db,
        page: int,
        page_size: int,
        search=None,
        status=None,
        payment_status=None
    ):

        orders, total = await OrderRepository.get_orders(
            db=db,
            page=page,
            page_size=page_size,
            search=search,
            status=status,
            payment_status=payment_status
        )

        summary = await OrderRepository.get_order_summary(db)

        return {
            "orders": [
                {
                    "id": str(order.id),

                    "order_number": order.order_number,

                    "products": [
                        {
                            "product_id": str(item.product_id),

                            "product_name": item.product_name,

                            "product_image": (
                                item.product.thumbnail_url
                                if item.product
                                else None
                            )
                        }
                        for item in order.items
                    ],

                    "customer_name": (
                        order.user.full_name
                        if order.user else None
                    ),

                    "customer_phone": (
                        order.user.phone
                        if order.user else None
                    ),

                    "items_count": len(order.items),

                    "amount": float(order.total_amount),

                    "payment_status": (
                        order.payment_status.value
                        if order.payment_status
                        else None
                    ),

                    "status": (
                        order.status.value
                        if order.status
                        else None
                    ),

                    "order_date": order.created_at
                }
                for order in orders
            ],

            "summary": {
                "total_orders": summary["total_orders"],
                "revenue": float(summary["revenue"]),
                "pending": summary["pending"] or 0,
                "in_transit": summary["in_transit"] or 0,
                "delivered": summary["delivered"] or 0,
                "cancelled": summary["cancelled"] or 0
            },

            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total
            }
        }

    @staticmethod
    async def get_order(
        db,
        order_id
    ):

        order = await OrderRepository.get_order_by_id(
            db,
            order_id
        )

        if not order:
            return None

        return {

            "id": str(order.id),

            "order_number": order.order_number,

            "order_date": order.created_at,

            "status": (
                order.status.value
                if order.status
                else None
            ),

            "payment_status": (
                order.payment_status.value
                if order.payment_status
                else None
            ),

            "customer": {

                "user_id": (
                    str(order.user.id)
                    if order.user else None
                ),

                "name": (
                    order.user.full_name
                    if order.user else None
                ),

                "phone": (
                    order.user.phone
                    if order.user else None
                ),

                "email": (
                    order.user.email
                    if order.user else None
                )
            },

            "shipping_address": {

                "address_id": (
                    str(order.address.id)
                    if order.address else None
                ),

                "full_name": (
                    order.address.full_name
                    if order.address else None
                ),

                "phone": (
                    order.address.phone
                    if order.address else None
                ),

                "address_line1": (
                    order.address.address_line1
                    if order.address else None
                ),

                "address_line2": (
                    order.address.address_line2
                    if order.address else None
                ),

                "city": (
                    order.address.city
                    if order.address else None
                ),

                "state": (
                    order.address.state
                    if order.address else None
                ),

                "pincode": (
                    order.address.pincode
                    if order.address else None
                ),

                "country": (
                    order.address.country
                    if order.address else None
                )
            },

            "address": {

                "address_id": (
                    str(order.address.id)
                    if order.address else None
                ),

                "full_name": (
                    order.address.full_name
                    if order.address else None
                ),

                "phone": (
                    order.address.phone
                    if order.address else None
                ),

                "address_line1": (
                    order.address.address_line1
                    if order.address else None
                ),

                "address_line2": (
                    order.address.address_line2
                    if order.address else None
                ),

                "city": (
                    order.address.city
                    if order.address else None
                ),

                "state": (
                    order.address.state
                    if order.address else None
                ),

                "pincode": (
                    order.address.pincode
                    if order.address else None
                ),

                "country": (
                    order.address.country
                    if order.address else None
                )
            },

            "items": [

                {
                    "order_item_id": str(item.id),

                    "product_id": str(item.product_id),

                    "product_name": item.product_name,

                    "product_sku": item.product_sku,

                    "product_image": (
                        item.product.thumbnail_url
                        if item.product
                        else None
                    ),

                    "quantity": item.quantity,

                    "price": float(item.price),

                    "gst_amount": float(item.gst_amount),

                    "total": float(item.total)
                }

                for item in order.items
            ],

            "pricing": {

                "subtotal": float(order.subtotal),

                "gst": float(order.gst_amount),

                "shipping": float(order.shipping_charge),

                "discount": float(order.discount),

                "grand_total": float(order.total_amount)
            },

            "payment": [

                {
                    "payment_id": str(payment.id),

                    "amount": float(payment.amount),

                    "method": (
                        payment.payment_method.value
                        if payment.payment_method
                        else None
                    ),

                    "transaction_id":
                        payment.gateway_transaction_id,

                    "status": (
                        payment.status.value
                        if payment.status
                        else None
                    ),

                    "paid_at": payment.paid_at
                }

                for payment in order.payments
            ],

            "cancel_reason": order.cancel_reason,

            "delivered_at": order.delivered_at,

            "shipment": (
                {
                    "courier_name": order.shipment.courier_name,
                    "awb_number": order.shipment.awb_number,
                    "status": order.shipment.status,
                    "shipped_at": order.shipment.shipped_at,
                    "estimated_delivery": order.shipment.estimated_delivery,
                    "label_url": order.shipment.label_url,
                    "raw_response": order.shipment.raw_response,
                }
                if order.shipment else None
            )
        }
    @staticmethod
    async def update_status(
        db,
        order_id,
        status
    ):

        return await OrderRepository.update_order_status(
            db,
            order_id,
            status
        )

    @staticmethod
    async def update_payment_status(
        db,
        order_id,
        payment_status
    ):

        return await OrderRepository.update_payment_status(
            db,
            order_id,
            payment_status
        )

    @staticmethod
    async def cancel_order(
        db,
        order_id,
        reason
    ):

        return await OrderRepository.cancel_order(
            db,
            order_id,
            reason
        )