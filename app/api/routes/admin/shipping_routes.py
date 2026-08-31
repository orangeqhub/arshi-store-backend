from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.repositories.order_repository import OrderRepository
from app.repositories.shipment_repository import ShipmentRepository
from app.schemas.admin.shipping_schema import ShipWithBlueDartRequest
from app.services.shipping.bluedart_client import (
    BlueDartAPIError,
    BlueDartAuthError,
)
from app.services.shipping.bluedart_service import (
    BlueDartConfigError,
    BlueDartDuplicateShipmentError,
    BlueDartService,
)

router = APIRouter(
    prefix="/admin/orders/{order_id}/shipping/bluedart",
    tags=["Admin Shipping - Blue Dart"],
    dependencies=[Depends(get_current_admin)],
)

diagnostics_router = APIRouter(
    prefix="/admin/shipping/bluedart",
    tags=["Admin Shipping - Blue Dart"],
    dependencies=[Depends(get_current_admin)],
)


def _raise_for(exc: Exception):

    if isinstance(exc, BlueDartConfigError):
        raise HTTPException(status_code=400, detail=str(exc))

    if isinstance(exc, BlueDartDuplicateShipmentError):
        raise HTTPException(status_code=409, detail=str(exc))

    if isinstance(exc, BlueDartAuthError):
        raise HTTPException(
            status_code=502,
            detail=f"Blue Dart auth failed: {exc}"
        )

    if isinstance(exc, BlueDartAPIError):
        raise HTTPException(
            status_code=502,
            detail=(
                f"Blue Dart API error: {exc}. "
                f"Response: {exc.response_body}"
            )
        )

    raise HTTPException(status_code=500, detail=str(exc))


def _serialize_shipment(shipment):

    return {
        "id": str(shipment.id),
        "courier_name": shipment.courier_name,
        "awb_number": shipment.awb_number,
        "status": shipment.status,
        "shipped_at": shipment.shipped_at,
        "estimated_delivery": shipment.estimated_delivery,
        "label_url": shipment.label_url,
        "raw_response": shipment.raw_response,
    }


@router.get("/serviceability")
async def check_serviceability(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
):

    order = await OrderRepository.get_order_by_id(db, order_id)

    if not order or not order.address:
        raise HTTPException(
            status_code=404,
            detail="Order or shipping address not found"
        )

    try:
        result = await BlueDartService.check_serviceability(
            order.address.pincode
        )
    except Exception as exc:
        _raise_for(exc)

    return {
        "success": True,
        "status_code": 200,
        "message": "Serviceability checked",
        "data": result,
    }


@router.post("/ship")
async def ship_with_bluedart(
    order_id: UUID,
    payload: ShipWithBlueDartRequest,
    db: AsyncSession = Depends(get_db),
):

    order = await OrderRepository.get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if not order.address:
        raise HTTPException(
            status_code=400,
            detail="Order has no shipping address"
        )

    try:
        await BlueDartService.check_serviceability(order.address.pincode)
    except Exception as exc:
        _raise_for(exc)

    try:
        shipment = await BlueDartService.ship_order(
            db,
            order,
            weight_kg=payload.weight_kg,
            pieces=payload.pieces,
        )
    except Exception as exc:
        _raise_for(exc)

    return {
        "success": True,
        "status_code": 201,
        "message": "Shipment created with Blue Dart",
        "data": _serialize_shipment(shipment),
    }


@router.get("/tracking")
async def get_tracking(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
):

    shipment = await ShipmentRepository.get_by_order_id(db, order_id)

    if not shipment or not shipment.awb_number:
        raise HTTPException(
            status_code=404,
            detail="No Blue Dart shipment found for this order"
        )

    try:
        shipment = await BlueDartService.refresh_tracking(db, shipment)
    except Exception as exc:
        _raise_for(exc)

    return {
        "success": True,
        "status_code": 200,
        "message": "Tracking updated",
        "data": _serialize_shipment(shipment),
    }


@diagnostics_router.get("/products")
async def list_bluedart_products():
    """
    Diagnostic endpoint: calls Blue Dart's GetAllProductsAndSubProducts so
    the admin can look up the exact ProductCode/SubProductCode values valid
    for this account, instead of guessing them.
    """

    try:
        result = await BlueDartService.list_products()
    except Exception as exc:
        _raise_for(exc)

    return {
        "success": True,
        "status_code": 200,
        "data": result,
    }
