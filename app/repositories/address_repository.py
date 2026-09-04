from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Address


class AddressRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        address: Address
    ):
        try:
            db.add(address)

            await db.commit()
            await db.refresh(address)

            return address

        except SQLAlchemyError:
            await db.rollback()
            raise

    @staticmethod
    async def get_user_addresses(
        db: AsyncSession,
        user_id: UUID
    ):
        result = await db.execute(
            select(Address)
            .where(
                Address.user_id == user_id,
                Address.is_deleted == False
            )
            .order_by(Address.created_at.desc())
        )

        return result.scalars().all()

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        address_id: UUID,
        user_id: UUID
    ):
        result = await db.execute(
            select(Address)
            .where(
                Address.id == address_id,
                Address.user_id == user_id,
                Address.is_deleted == False
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def update(
        db: AsyncSession,
        address: Address
    ):
        try:
            await db.commit()
            await db.refresh(address)

            return address

        except SQLAlchemyError:
            await db.rollback()
            raise

    @staticmethod
    async def delete(
        db: AsyncSession,
        address: Address
    ):
        try:
            # Soft Delete
            address.is_deleted = True

            await db.commit()
            await db.refresh(address)

            return address

        except SQLAlchemyError:
            await db.rollback()
            raise