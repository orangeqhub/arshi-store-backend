from app.repositories.setting_repository import (
    SettingRepository
)


class SettingService:

    @staticmethod
    async def get_general_settings(
        db
    ):
        settings = (
            await SettingRepository
            .get_settings(db)
        )

        return {
            "admin_display_name":
                settings.company_name,
            "support_email":
                settings.support_email,
            "timezone":
                settings.timezone
        }

    @staticmethod
    async def update_general_settings(
        db,
        request
    ):
        settings = (
            await SettingRepository
            .get_settings(db)
        )

        settings.company_name = (
            request.admin_display_name
        )

        settings.support_email = (
            request.support_email
        )

        settings.timezone = (
            request.timezone
        )

        await SettingRepository.save(
            db,
            settings
        )

        return settings

    @staticmethod
    async def get_store_settings(
        db
    ):
        settings = (
            await SettingRepository
            .get_settings(db)
        )

        return {
            "business_name":
                settings.company_name,
            "phone":
                settings.support_phone,
            "gst_number":
                settings.gst_number,
            "address":
                settings.address
        }

    @staticmethod
    async def update_store_settings(
        db,
        request
    ):
        settings = (
            await SettingRepository
            .get_settings(db)
        )

        settings.company_name = (
            request.business_name
        )

        settings.support_phone = (
            request.phone
        )

        settings.gst_number = (
            request.gst_number
        )

        settings.address = (
            request.address
        )

        await SettingRepository.save(
            db,
            settings
        )

        return settings

    @staticmethod
    async def get_delivery_settings(
        db
    ):
        settings = (
            await SettingRepository
            .get_settings(db)
        )

        return {
            "delivery_charge":
                settings.delivery_charge,
            "free_shipping_threshold":
                settings.free_shipping_threshold,
            "cod_charge":
                settings.cod_charge
        }

    @staticmethod
    async def update_delivery_settings(
        db,
        request
    ):
        settings = (
            await SettingRepository
            .get_settings(db)
        )

        settings.delivery_charge = (
            request.delivery_charge
        )

        settings.free_shipping_threshold = (
            request.free_shipping_threshold
        )

        settings.cod_charge = (
            request.cod_charge
        )

        await SettingRepository.save(
            db,
            settings
        )

        return settings