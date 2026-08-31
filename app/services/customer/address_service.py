from sqlalchemy.exc import SQLAlchemyError

from app.models.models import Address
from app.repositories.address_repository import AddressRepository


class AddressService:

    @staticmethod
    def _serialize_address(address):
        return {
            "id": str(address.id),
            "full_name": address.full_name,
            "email": address.email,
            "phone": address.phone,
            "address_line1": address.address_line1,
            "address_line2": address.address_line2,
            "landmark": address.landmark,
            "city": address.city,
            "state": address.state,
            "pincode": address.pincode,
            "country": address.country,
            "address_type": address.address_type,
            "is_default": address.is_default,
        }

    @staticmethod
    async def create_address(
        db,
        user_id,
        payload
    ):
        try:
            address = Address(
                user_id=user_id,
                full_name=payload.full_name,
                email=payload.email,
                phone=payload.phone,
                address_line1=payload.address_line1,
                address_line2=payload.address_line2,
                landmark=payload.landmark,
                city=payload.city,
                state=payload.state,
                pincode=payload.pincode,
                country=payload.country,
                address_type=payload.address_type,
                is_default=payload.is_default
            )

            address = await AddressRepository.create(
                db,
                address
            )

            return {
                "success": True,
                "status_code": 201,
                "message": "Address created successfully",
                "data": {
                    "id": str(address.id)
                }
            }

        except SQLAlchemyError:
            return {
                "success": False,
                "status_code": 500,
                "message": "Failed to create address"
            }

    @staticmethod
    async def get_addresses(
        db,
        user_id
    ):
        try:
            addresses = await AddressRepository.get_user_addresses(
                db,
                user_id
            )

            return {
                "success": True,
                "status_code": 200,
                "data": [
                    AddressService._serialize_address(address)
                    for address in addresses
                ]
            }

        except SQLAlchemyError:
            return {
                "success": False,
                "status_code": 500,
                "message": "Failed to fetch addresses"
            }

    @staticmethod
    async def get_address(
        db,
        user_id,
        address_id
    ):
        try:
            address = await AddressRepository.get_by_id(
                db,
                address_id,
                user_id
            )

            if not address:
                return {
                    "success": False,
                    "status_code": 404,
                    "message": "Address not found"
                }

            return {
                "success": True,
                "status_code": 200,
                "data": AddressService._serialize_address(address)
            }

        except SQLAlchemyError:
            return {
                "success": False,
                "status_code": 500,
                "message": "Failed to fetch address"
            }

    @staticmethod
    async def update_address(
        db,
        user_id,
        address_id,
        payload
    ):
        try:
            address = await AddressRepository.get_by_id(
                db,
                address_id,
                user_id
            )

            if not address:
                return {
                    "success": False,
                    "status_code": 404,
                    "message": "Address not found"
                }

            address.full_name = payload.full_name
            address.email = getattr(payload, "email", address.email)
            address.phone = payload.phone
            address.address_line1 = payload.address_line1
            address.address_line2 = payload.address_line2
            address.landmark = getattr(payload, "landmark", address.landmark)
            address.city = payload.city
            address.state = payload.state
            address.pincode = payload.pincode
            address.country = payload.country
            address.address_type = getattr(payload, "address_type", address.address_type)
            address.is_default = payload.is_default

            await AddressRepository.update(
                db,
                address
            )

            return {
                "success": True,
                "status_code": 200,
                "message": "Address updated successfully"
            }

        except SQLAlchemyError:
            return {
                "success": False,
                "status_code": 500,
                "message": "Failed to update address"
            }

    @staticmethod
    async def delete_address(
        db,
        user_id,
        address_id
    ):
        try:
            address = await AddressRepository.get_by_id(
                db,
                address_id,
                user_id
            )

            if not address:
                return {
                    "success": False,
                    "status_code": 404,
                    "message": "Address not found"
                }

            await AddressRepository.delete(
                db,
                address
            )

            return {
                "success": True,
                "status_code": 200,
                "message": "Address deleted successfully"
            }

        except SQLAlchemyError:
            return {
                "success": False,
                "status_code": 500,
                "message": "Failed to delete address"
            }