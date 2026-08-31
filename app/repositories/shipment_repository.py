from sqlalchemy import select

from app.models.models import Shipment


class ShipmentRepository:

    @staticmethod
    async def get_by_order_id(db, order_id):

        result = await db.execute(
            select(Shipment).where(
                Shipment.order_id == order_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_awb(db, awb_number):

        result = await db.execute(
            select(Shipment).where(
                Shipment.awb_number == awb_number
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def upsert_for_order(
        db,
        order_id,
        courier_name,
        awb_number,
        tracking_number,
        status,
        raw_response,
        shipped_at,
        label_url=None,
    ):

        shipment = await ShipmentRepository.get_by_order_id(
            db,
            order_id
        )

        if not shipment:
            shipment = Shipment(order_id=order_id)
            db.add(shipment)

        shipment.courier_name = courier_name
        shipment.awb_number = awb_number
        shipment.tracking_number = tracking_number
        shipment.status = status
        shipment.raw_response = raw_response
        shipment.label_url = label_url
        shipment.shipped_at = shipped_at

        await db.commit()
        await db.refresh(shipment)

        return shipment

    @staticmethod
    async def update_tracking(
        db,
        shipment,
        status,
        raw_response,
        estimated_delivery=None,
    ):

        shipment.status = status
        shipment.raw_response = raw_response

        if estimated_delivery:
            shipment.estimated_delivery = estimated_delivery

        await db.commit()
        await db.refresh(shipment)

        return shipment
