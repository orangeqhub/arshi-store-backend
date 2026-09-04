from sqlalchemy import select

from app.models.models import StoreSetting

from sqlalchemy import select

from app.models.models import (
    StoreSetting
)


from sqlalchemy import select

from app.models.models import (
    StoreSetting
)


class SettingRepository:

    @staticmethod
    async def get_settings(
        db
    ):
        result = await db.execute(
            select(StoreSetting)
        )

        settings = result.scalar_one_or_none()

        if settings:
            return settings

        settings = StoreSetting(
            company_name="Surgical World",
            support_email="support@surgicalworld.in",
            support_phone="",
            address="",
            gst_number="",
            delivery_charge=0,
            free_shipping_threshold=0,
            cod_charge=0,
            currency="INR",
            timezone="Asia/Kolkata"
        )

        db.add(settings)

        await db.commit()

        await db.refresh(settings)

        return settings

    @staticmethod
    async def save(
        db,
        settings
    ):
        await db.commit()
        await db.refresh(settings)

        return settings