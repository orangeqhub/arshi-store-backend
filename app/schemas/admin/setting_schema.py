from pydantic import BaseModel
from decimal import Decimal


class UpdateGeneralSettingsRequest(
    BaseModel
):
    admin_display_name: str
    support_email: str
    timezone: str


class UpdateStoreSettingsRequest(
    BaseModel
):
    business_name: str
    phone: str
    gst_number: str
    address: str


class UpdateDeliverySettingsRequest(
    BaseModel
):
    delivery_charge: Decimal
    free_shipping_threshold: Decimal
    cod_charge: Decimal