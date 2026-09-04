"""
Blue Dart business logic: maps Order + Address + OrderItems + Payment into
a GenerateWayBill request, and wraps serviceability / product-lookup /
tracking calls.

NOTE ON GenerateWayBill PAYLOAD:
Field names below (Consignee / Shipper / Services / Profile blocks) follow
Blue Dart's documented GenerateWayBill schema. The "Profile" block
(LoginID / LicenceKey / Api_type) matches exactly what was confirmed for
this project, with top-level "Profile" capitalized as documented.
CustomerCode, OriginArea, ProductCode and SubProductCode are account-specific
and are read only from settings (never hardcoded) - see
REQUIRED_CONFIG_FIELDS below for what must be filled in .env before this
will work.

NOTE ON THE COD AMOUNT FIELD:
Blue Dart's documented GenerateWayBill schema spells this field
"CollactableAmount" (not "CollectableAmount") - that is the exact,
documented spelling used below for the sandbox payload, not a guess.

NOTE ON PickupDate/PickupTime:
GenerateWayBill uses a different format from the Transit Time API:
PickupDate is "/Date(<unix epoch milliseconds>)/" and PickupTime is
"HHmm" (e.g. "1400") - confirmed against the Blue Dart documentation
supplied for this project. Do not reuse the Transit API's
"/Date(ms)/" + "HH:mm" pairing verbatim without checking the PickupTime
separator, since only PickupDate shares the same "/Date(ms)/" wrapper
between the two APIs.

NOTE ON RESPONSE PARSING:
The exact JSON key Blue Dart uses for the returned AWB number was not
supplied in the project brief. `_extract_awb_number` checks the common
candidates; if none match, the full raw response is preserved in the
raised error so the correct key can be added in one place.

NOTE ON THE "<MethodName>Result" WRAPPER:
Every Blue Dart API actually tested live for this project so far
(GetServicesforPincode, GetAllProductsAndSubProducts,
GetDomesticTransitTimeForPinCodeandProduct) wraps its payload in a
"<MethodName>Result" object. GenerateWayBill has never been called live,
so `_unwrap_generate_waybill_result` normalizes both possibilities
(wrapped under "GenerateWayBillResult", or already flat) before AWB
number / status / label extraction run - the full, un-normalized response
is still what gets persisted to `raw_response` for auditing.

NOTE ON ERROR DETECTION:
`GetServicesforPincode`/`GetDomesticTransitTimeForPinCodeandProduct` both
returned "ErrorMessage": "Valid" with "IsError": false on a *successful*
call (confirmed live) - so a non-empty "ErrorMessage" is not itself proof
of failure. `_is_bluedart_error` treats the response as an error only when
"IsError" is explicitly true, or "ErrorMessage" is present and is not the
known "Valid" success sentinel.

NOTE ON THE LABEL PDF:
Per the confirmed spec, a successful GenerateWayBill response carries the
label as base64 PDF bytes in "AWBPrintContent". `_save_label_pdf` decodes
and writes it under uploads/shipping-labels/<awb>.pdf (same convention as
LocalStorage.upload_product_image), so it's servable via the existing
/uploads static mount without a new endpoint.

NOTE ON THE IDEMPOTENCY GUARD AND ATTEMPT STATE MACHINE:
`ship_order` looks up any existing Shipment row for this order (by
order_id, the same column the DB's UNIQUE(order_id) constraint protects)
before ever building the payload or calling GenerateWayBill - order.id is
the reference used to identify "this order" for that check (order_number
appears in the payload/logs for human readability).

A Shipment row moves through these non-awb statuses around a
GenerateWayBill attempt:
  - STATUS_IN_PROGRESS: persisted BEFORE calling Blue Dart, and again
    immediately after a raw response is received (before any extraction
    is attempted). If a crash/timeout happens while in this state, the
    outcome is genuinely unknown, so it BLOCKS all further attempts.
  - STATUS_UNRESOLVED: Blue Dart replied with no explicit error, but no
    recognizable AWB number could be found. We cannot assume no shipment
    was created, so this permanently BLOCKS further automatic attempts
    until resolved by hand.
  - STATUS_FAILED: Blue Dart explicitly rejected the request (IsError, or
    a non-"Valid" ErrorMessage) with no AWB present. This does NOT block -
    a corrected retry is allowed - but is never auto-retried by this code.
A shipment with an awb_number always blocks further attempts, regardless
of status.
"""

import base64
from datetime import datetime, timezone

from app.core.config import settings
from app.core.storage import get_upload_root
from app.models.models import PaymentMethod
from app.repositories.shipment_repository import ShipmentRepository
from app.services.shipping.bluedart_client import (
    BlueDartAPIError,
    BlueDartClient,
)


class BlueDartConfigError(Exception):
    pass


class BlueDartDuplicateShipmentError(Exception):
    pass


# Non-AWB Shipment.status values used while a GenerateWayBill attempt is
# in flight or could not be cleanly resolved - see the module docstring.
STATUS_IN_PROGRESS = "AWB_REQUEST_IN_PROGRESS"
STATUS_UNRESOLVED = "AWB_RESPONSE_UNRESOLVED"
STATUS_FAILED = "AWB_REQUEST_FAILED"


REQUIRED_CONFIG_FIELDS = [
    "BLUEDART_CUSTOMER_CODE",
    "BLUEDART_ORIGIN_AREA",
    "BLUEDART_PRODUCT_CODE",
    "BLUEDART_SHIPPER_NAME",
    "BLUEDART_SHIPPER_ADDRESS1",
    "BLUEDART_SHIPPER_CITY",
    "BLUEDART_SHIPPER_PINCODE",
    "BLUEDART_SHIPPER_PHONE",
]


def _ensure_configured():

    missing = [
        field
        for field in REQUIRED_CONFIG_FIELDS
        if not getattr(settings, field, None)
    ]

    if missing:
        raise BlueDartConfigError(
            "Blue Dart is not fully configured. Missing .env values: "
            + ", ".join(missing)
        )


def _extract_awb_number(response: dict) -> str | None:

    if not isinstance(response, dict):
        return None

    for key in (
        "AWBNo",
        "AWBNumber",
        "awb_no",
        "awbNo",
        "AwbNumber",
        "WaybillNumber",
    ):
        value = response.get(key)
        if value:
            return str(value)

    return None


def _extract_status(response: dict, fallback: str | None = None) -> str | None:

    if not isinstance(response, dict):
        return fallback

    # Handle tracking response structure: {"ShipmentData": {"Shipment": [{"Status": "..."}]}}
    shipment_data = response.get("ShipmentData")
    if isinstance(shipment_data, dict):
        shipments = shipment_data.get("Shipment")
        if isinstance(shipments, list) and len(shipments) > 0:
            ship_detail = shipments[0]
            if isinstance(ship_detail, dict):
                raw_status = ship_detail.get("Status")
                if isinstance(raw_status, str):
                    status_lower = raw_status.strip().lower()
                    if "delivered" in status_lower:
                        return "DELIVERED"
                    elif "out for delivery" in status_lower:
                        return "OUT_FOR_DELIVERY"
                    elif "in transit" in status_lower:
                        return "IN_TRANSIT"
                    elif "picked up" in status_lower:
                        return "SHIPPED"
                    elif "pickup has been registered" in status_lower:
                        return "PICKUP_REGISTERED"
                    elif "waybill" in status_lower or "booked" in status_lower:
                        return "WAYBILL_GENERATED"
                    else:
                        return raw_status

    # Check for "Status" key specifically first to handle list format
    status_val = response.get("Status")
    if isinstance(status_val, list):
        has_pickup_registration_valid = False
        for item in status_val:
            if isinstance(item, dict):
                sc = item.get("StatusCode")
                if isinstance(sc, str) and "Pickup Registration:Valid" in sc:
                    has_pickup_registration_valid = True
                    break
        if has_pickup_registration_valid:
            return "PICKUP_REGISTERED"
        else:
            return "WAYBILL_GENERATED"

    for key in ("Status", "status", "ScanStatus", "CurrentStatus"):
        value = response.get(key)
        if value:
            if isinstance(value, list):
                continue
            return str(value)

    return fallback


GENERATE_WAYBILL_RESULT_KEY = "GenerateWayBillResult"


def _unwrap_generate_waybill_result(raw_response: dict) -> dict:
    """
    GenerateWayBill's success/error shape has never been called live, but
    every other tested Blue Dart API wraps its payload in a
    "<MethodName>Result" object. Use that wrapper if present, otherwise
    fall back to treating the response itself as the result.
    """

    if not isinstance(raw_response, dict):
        return {}

    wrapped = raw_response.get(GENERATE_WAYBILL_RESULT_KEY)

    if isinstance(wrapped, dict):
        return wrapped

    return raw_response


def _is_bluedart_error(result: dict) -> tuple[bool, str | None]:
    """
    Returns (is_error, message). "IsError": true is always an error.
    A non-empty "ErrorMessage" is only treated as an error if it isn't the
    known "Valid" success sentinel confirmed on other Blue Dart endpoints -
    see the module docstring.
    """

    if not isinstance(result, dict):
        return True, "Empty or non-JSON Blue Dart response"

    if result.get("IsError") is True:
        return True, result.get("ErrorMessage") or "Blue Dart reported IsError=true"

    error_message = result.get("ErrorMessage")

    if error_message and error_message != "Valid":
        return True, error_message

    return False, None


class BlueDartService:

    client = BlueDartClient()

    @staticmethod
    async def check_serviceability(pincode: str) -> dict:

        return await BlueDartService.client.get_services_for_pincode(pincode)

    @staticmethod
    async def list_products() -> dict:

        return await BlueDartService.client.get_all_products_and_subproducts()

    @staticmethod
    def _build_waybill_payload(
        order,
        weight_kg: float,
        pieces: int,
    ) -> dict:

        address = order.address
        item_description = ", ".join(
            item.product_name for item in order.items
        )[:200] or "Homemade food products"

        return {
            "Request": {
                "Consignee": {
                    "ConsigneeName": address.full_name,
                    "ConsigneeAddress1": address.address_line1,
                    "ConsigneeAddress2": address.address_line2 or "",
                    "ConsigneeAddress3": address.landmark or "",
                    "ConsigneePincode": int(address.pincode),
                    "ConsigneeMobile": address.phone,
                    "ConsigneeTelephone": address.phone,
                    "ConsigneeEmailID": address.email or "",
                    "ConsigneeAttention": address.full_name,
                },
                "Shipper": {
                    "CustomerCode": settings.BLUEDART_CUSTOMER_CODE,
                    "CustomerName": settings.BLUEDART_SHIPPER_NAME,
                    "CustomerAddress1": settings.BLUEDART_SHIPPER_ADDRESS1,
                    "CustomerAddress2": settings.BLUEDART_SHIPPER_ADDRESS2 or "",
                    "CustomerPincode": int(settings.BLUEDART_SHIPPER_PINCODE),
                    "CustomerMobile": settings.BLUEDART_SHIPPER_PHONE,
                    "CustomerTelephone": settings.BLUEDART_SHIPPER_PHONE,
                    "CustomerEmailID": settings.BLUEDART_SHIPPER_EMAIL or "",
                    "OriginArea": settings.BLUEDART_ORIGIN_AREA,
                    "Sender": settings.BLUEDART_SHIPPER_NAME,
                    # Normal Arshi outbound shipment: freight billed to the
                    # shipper's own Blue Dart account, not the consignee.
                    "IsToPayCustomer": False,
                },
                "Services": {
                    "ProductCode": settings.BLUEDART_PRODUCT_CODE,
                    "SubProductCode": "P",
                    # Physical merchandise (Dutiables) = 1, Documents = 0.
                    "ProductType": 1,
                    "ActualWeight": weight_kg,
                    "PieceCount": pieces,
                    "ItemCount": pieces,
                    "CollactableAmount": 0.0,
                    # Goods/merchandise value only - excludes shipping_charge.
                    "DeclaredValue": float(order.subtotal),
                    "CreditReferenceNo": order.order_number,
                    "CustomerReferenceNo": order.order_number,
                    "Commodity": {
                        "CommodityDetail1": item_description,
                    },
                    "PickupDate": (
                        f"/Date({int(datetime.now(timezone.utc).timestamp() * 1000)})/"
                    ),
                    "PickupTime": "1400",
                    # Normal outbound shipment, not a customer-return pickup.
                    "IsReversePickup": False,
                    # Register a pickup with Blue Dart as soon as the AWB is
                    # created, so a courier actually gets dispatched.
                    "RegisterPickup": True,
                    # IsForcePickup bypasses Blue Dart's normal pickup-slot/
                    # cutoff constraints - not appropriate as a default for a
                    # routine admin "Ship with Blue Dart" action, only for a
                    # genuine forced/urgent case, so it stays false here.
                    "IsForcePickup": False,
                    "AWBNo": "",
                    "Dimensions": [],
                    "ECCN": "",
                    "PDFOutputNotRequired": False,
                    "PackType": "",
                    "SpecialInstruction": "",
                    "itemdtl": [],
                    "noOfDCGiven": 0,
                },
                "Returnadds": {
                    "ManifestNumber": "",
                    "ReturnAddress1": settings.BLUEDART_SHIPPER_ADDRESS1,
                    "ReturnAddress2": settings.BLUEDART_SHIPPER_ADDRESS2 or "",
                    "ReturnAddress3": "",
                    "ReturnContact": settings.BLUEDART_SHIPPER_NAME,
                    "ReturnPincode": int(settings.BLUEDART_SHIPPER_PINCODE),
                    "ReturnMobile": settings.BLUEDART_SHIPPER_PHONE,
                    "ReturnTelephone": settings.BLUEDART_SHIPPER_PHONE,
                    "ReturnEmailID": settings.BLUEDART_SHIPPER_EMAIL or "",
                },
            },
            "Profile": {
                "LoginID": settings.BLUEDART_LOGIN_ID,
                "LicenceKey": settings.BLUEDART_LICENCE_KEY,
                "Api_type": settings.BLUEDART_API_TYPE,
            },
        }

    @staticmethod
    def _save_label_pdf(awb_number: str, result: dict) -> str | None:

        content = (
            result.get("AWBPrintContent")
            if isinstance(result, dict)
            else None
        )

        if not content:
            return None

        if isinstance(content, list):
            try:
                pdf_bytes = bytes(content)
            except (ValueError, TypeError):
                return None
        elif isinstance(content, str):
            try:
                pdf_bytes = base64.b64decode(content)
            except (ValueError, TypeError):
                return None
        elif isinstance(content, (bytes, bytearray)):
            pdf_bytes = content
        else:
            return None

        labels_dir = get_upload_root() / "shipping-labels"
        labels_dir.mkdir(parents=True, exist_ok=True)

        file_path = labels_dir / f"{awb_number}.pdf"

        with open(file_path, "wb") as f:
            f.write(pdf_bytes)

        site_url = settings.SITE_URL.rstrip("/")

        return f"{site_url}/uploads/shipping-labels/{awb_number}.pdf"

    @staticmethod
    async def ship_order(
        db,
        order,
        weight_kg: float,
        pieces: int = 1,
    ):

        _ensure_configured()

        if not order.address:
            raise BlueDartConfigError(
                "Order has no shipping address"
            )

        # Idempotency guard - block a fresh GenerateWayBill call whenever:
        #   - an AWB was already recorded (a shipment already exists), or
        #   - the previous attempt's outcome is unknown/unresolved
        #     (STATUS_IN_PROGRESS: we sent a request and never confirmed
        #     what happened; STATUS_UNRESOLVED: Blue Dart replied with no
        #     error but we couldn't recognize an AWB in it).
        # STATUS_FAILED (a clean, explicit Blue Dart business rejection,
        # confirmed no AWB was created) is deliberately NOT blocking, so a
        # corrected retry is possible - see the module docstring.
        existing_shipment = await ShipmentRepository.get_by_order_id(
            db,
            order.id
        )

        if existing_shipment and (
            existing_shipment.awb_number
            or existing_shipment.status in (
                STATUS_IN_PROGRESS,
                STATUS_UNRESOLVED,
            )
        ):
            raise BlueDartDuplicateShipmentError(
                "Blue Dart shipment already exists for this order."
            )

        # Persist an in-progress attempt record BEFORE calling Blue Dart.
        # If the process crashes/times out between sending the request and
        # getting a reply, this committed row blocks any further attempt
        # until someone manually investigates - we cannot assume Blue Dart
        # did NOT create a shipment for a request we never got a reply to.
        shipment = await ShipmentRepository.upsert_for_order(
            db,
            order_id=order.id,
            courier_name="Blue Dart",
            awb_number=None,
            tracking_number=None,
            status=STATUS_IN_PROGRESS,
            raw_response=None,
            label_url=None,
            shipped_at=None,
        )

        payload = BlueDartService._build_waybill_payload(
            order=order,
            weight_kg=weight_kg,
            pieces=pieces,
        )

        try:
            raw_response = await BlueDartService.client.generate_waybill(payload)
        except BlueDartAPIError as e:
            if e.status_code and 400 <= e.status_code < 500:
                status = STATUS_FAILED
            else:
                status = STATUS_IN_PROGRESS
            await ShipmentRepository.upsert_for_order(
                db,
                order_id=order.id,
                courier_name="Blue Dart",
                awb_number=None,
                tracking_number=None,
                status=status,
                raw_response=e.response_body,
                label_url=None,
                shipped_at=None,
            )
            raise e
        except Exception as e:
            await ShipmentRepository.upsert_for_order(
                db,
                order_id=order.id,
                courier_name="Blue Dart",
                awb_number=None,
                tracking_number=None,
                status=STATUS_IN_PROGRESS,
                raw_response={"error": type(e).__name__, "message": str(e)},
                label_url=None,
                shipped_at=None,
            )
            raise e

        # Always persist the full raw response immediately, before any
        # extraction is attempted - this is the fix for the exact gap
        # that could leave a real, successful-but-unrecognized AWB
        # response completely unrecorded.
        shipment = await ShipmentRepository.upsert_for_order(
            db,
            order_id=order.id,
            courier_name="Blue Dart",
            awb_number=None,
            tracking_number=None,
            status=STATUS_IN_PROGRESS,
            raw_response=raw_response,
            label_url=None,
            shipped_at=None,
        )

        result = _unwrap_generate_waybill_result(raw_response)

        is_error, error_message = _is_bluedart_error(result)

        if is_error:
            # Explicit, clean business rejection - Blue Dart told us the
            # request was rejected, so no AWB exists. Marked as FAILED
            # (not blocking) rather than UNRESOLVED, so a corrected retry
            # is possible. No automatic retry happens here regardless.
            await ShipmentRepository.upsert_for_order(
                db,
                order_id=order.id,
                courier_name="Blue Dart",
                awb_number=None,
                tracking_number=None,
                status=STATUS_FAILED,
                raw_response=raw_response,
                label_url=None,
                shipped_at=None,
            )

            raise BlueDartAPIError(
                f"Blue Dart GenerateWayBill returned an error: {error_message}",
                response_body=raw_response,
            )

        awb_number = _extract_awb_number(result)

        if not awb_number:
            # Ambiguous: no error was reported, but no recognizable AWB
            # number either. We cannot assume no shipment was created, so
            # this is UNRESOLVED and permanently blocks further automatic
            # attempts (see the idempotency guard above) until resolved
            # by hand.
            await ShipmentRepository.upsert_for_order(
                db,
                order_id=order.id,
                courier_name="Blue Dart",
                awb_number=None,
                tracking_number=None,
                status=STATUS_UNRESOLVED,
                raw_response=raw_response,
                label_url=None,
                shipped_at=None,
            )

            raise BlueDartAPIError(
                "Blue Dart reported no error but the response did not "
                "include a recognizable AWB number. This order is now "
                "blocked from further automatic Ship attempts - the full "
                "response is attached for manual review, and the correct "
                "field name can be added to "
                "bluedart_service._extract_awb_number.",
                response_body=raw_response,
            )

        label_url = BlueDartService._save_label_pdf(awb_number, result)

        shipment = await ShipmentRepository.upsert_for_order(
            db,
            order_id=order.id,
            courier_name="Blue Dart",
            awb_number=awb_number,
            tracking_number=awb_number,
            status=_extract_status(result, fallback="booked"),
            raw_response=raw_response,
            label_url=label_url,
            shipped_at=datetime.now(timezone.utc),
        )

        return shipment

    @staticmethod
    async def track(awb_number: str) -> dict:

        return await BlueDartService.client.track_shipment(awb_number)

    @staticmethod
    async def refresh_tracking(db, shipment):
        from app.models.models import OrderStatus

        def map_shipment_to_order_status(shipment_status: str) -> OrderStatus | None:
            status_upper = shipment_status.upper()
            if status_upper == "DELIVERED":
                return OrderStatus.DELIVERED
            elif status_upper == "OUT_FOR_DELIVERY":
                return OrderStatus.OUT_FOR_DELIVERY
            elif status_upper in ("SHIPPED", "IN_TRANSIT"):
                return OrderStatus.SHIPPED
            return None

        try:
            response = await BlueDartService.track(shipment.awb_number)
            status = _extract_status(response, fallback=shipment.status)

            order = None
            if shipment.order_id:
                from app.models.models import Order
                from sqlalchemy import select
                res_order = await db.execute(select(Order).where(Order.id == shipment.order_id))
                order = res_order.scalar_one_or_none()

            if order:
                new_order_status = map_shipment_to_order_status(status)
                if new_order_status and order.status != new_order_status:
                    order.status = new_order_status
                    if new_order_status == OrderStatus.DELIVERED:
                        order.delivered_at = datetime.now(timezone.utc)

            shipment = await ShipmentRepository.update_tracking(
                db,
                shipment=shipment,
                status=status,
                raw_response=response,
            )
        except Exception as e:
            # Safe handling: do not change status, just log
            print(f"Error during refresh_tracking for AWB {shipment.awb_number}: {e}", flush=True)
            pass

        return shipment

    @staticmethod
    async def sync_all_trackings():
        from app.models.models import Shipment, Order, OrderStatus
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select, text
        from app.core.database import engine, AsyncSessionLocal

        # 1. Check out a single physical connection to ensure session lock safety
        async with engine.connect() as conn:
            try:
                # 2. Acquire advisory lock on this connection
                lock_res = await conn.execute(text("SELECT pg_try_advisory_lock(4882981836)"))
                lock_acquired = lock_res.scalar()
                if not lock_acquired:
                    # Lock is held by another worker, skip this execution run
                    return
            except Exception as e:
                print(f"Failed to acquire advisory lock: {e}")
                return

            try:
                # 3. Use standard AsyncSessionLocal for db operations (will manage its own commits correctly)
                async with AsyncSessionLocal() as db:
                    stmt = (
                        select(Shipment)
                        .join(Order, Shipment.order_id == Order.id)
                        .options(selectinload(Shipment.order))
                        .where(Shipment.awb_number.isnot(None))
                        .where(Shipment.status != "DELIVERED")
                        .where(Order.status != OrderStatus.DELIVERED)
                        .where(Order.status != OrderStatus.CANCELLED)
                    )
                    result = await db.execute(stmt)
                    shipments = result.scalars().all()

                    for shipment in shipments:
                        try:
                            await BlueDartService.refresh_tracking(db, shipment)
                        except Exception as e:
                            print(f"Failed to sync tracking for AWB {shipment.awb_number}: {e}")
            except Exception as e:
                print(f"Error in sync_all_trackings scheduler job: {e}")
            finally:
                # 4. Always release the advisory lock on the exact same physical connection
                try:
                    await conn.execute(text("SELECT pg_advisory_unlock(4882981836)"))
                except Exception as e:
                    print(f"Failed to release advisory lock: {e}")


import asyncio

async def tracking_scheduler_loop():
    # Delay initial run slightly to let startup finish
    await asyncio.sleep(5)
    while True:
        try:
            await BlueDartService.sync_all_trackings()
        except Exception as e:
            print(f"Background tracking scheduler error: {e}")
        # Run every 15 minutes
        await asyncio.sleep(15 * 60)
