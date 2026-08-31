from app.models.models import Coupon

from app.repositories.coupon_repository import (
    CouponRepository
)


class CouponService:

    @staticmethod
    async def create_coupon(
        db,
        payload
    ):

        existing = await CouponRepository.get_by_code(
            db,
            payload.code.upper()
        )

        if existing:
            return {
                "success": False,
                "status_code": 400,
                "message": "Coupon code already exists"
            }

        coupon = Coupon(
            code=payload.code.upper(),
            title=payload.title,
            description=payload.description,

            # IMPORTANT
            coupon_type=payload.coupon_type.value
            if hasattr(payload.coupon_type, "value")
            else payload.coupon_type,

            discount_value=payload.discount_value,
            max_discount_amount=payload.max_discount_amount,
            minimum_order_amount=payload.minimum_order_amount,
            usage_limit=payload.usage_limit,
            is_first_order_only=payload.is_first_order_only,
            valid_from=payload.valid_from,
            valid_until=payload.valid_until
        )

        coupon = await CouponRepository.create(
            db,
            coupon
        )

        return {
            "success": True,
            "status_code": 201,
            "message": "Coupon created successfully",
            "data": {
                "id": str(coupon.id),
                "code": coupon.code,
                "coupon_type": coupon.coupon_type
            }
        }

    @staticmethod
    async def get_coupons(
        db
    ):

        coupons = await CouponRepository.get_all(
            db
        )

        return {
            "success": True,
            "status_code": 200,
            "message": "Coupons fetched successfully",
            "data": coupons
        }

    @staticmethod
    async def get_coupon(
        db,
        coupon_id
    ):

        coupon = await CouponRepository.get_by_id(
            db,
            coupon_id
        )

        if not coupon:
            return {
                "success": False,
                "status_code": 404,
                "message": "Coupon not found"
            }

        return {
            "success": True,
            "status_code": 200,
            "message": "Coupon fetched successfully",
            "data": coupon
        }

    @staticmethod
    async def update_coupon(
        db,
        coupon_id,
        payload
    ):

        coupon = await CouponRepository.get_by_id(
            db,
            coupon_id
        )

        if not coupon:
            return {
                "success": False,
                "status_code": 404,
                "message": "Coupon not found"
            }

        update_data = payload.model_dump(
            exclude_unset=True
        )

        if "coupon_type" in update_data:
            coupon_type = update_data["coupon_type"]

            update_data["coupon_type"] = (
                coupon_type.value
                if hasattr(coupon_type, "value")
                else coupon_type
            )

        for key, value in update_data.items():

            setattr(
                coupon,
                key,
                value
            )

        await CouponRepository.update(
            db,
            coupon
        )

        return {
            "success": True,
            "status_code": 200,
            "message": "Coupon updated successfully"
        }

    @staticmethod
    async def delete_coupon(
        db,
        coupon_id
    ):

        coupon = await CouponRepository.get_by_id(
            db,
            coupon_id
        )

        if not coupon:
            return {
                "success": False,
                "status_code": 404,
                "message": "Coupon not found"
            }

        await CouponRepository.delete(
            db,
            coupon
        )

        return {
            "success": True,
            "status_code": 200,
            "message": "Coupon deleted successfully"
        }

    @staticmethod
    async def update_coupon_status(
        db,
        coupon_id,
        is_active
    ):

        coupon = await CouponRepository.get_by_id(
            db,
            coupon_id
        )

        if not coupon:
            return {
                "success": False,
                "status_code": 404,
                "message": "Coupon not found"
            }

        coupon.is_active = is_active

        await CouponRepository.update(
            db,
            coupon
        )

        return {
            "success": True,
            "status_code": 200,
            "message": "Coupon status updated successfully"
        }