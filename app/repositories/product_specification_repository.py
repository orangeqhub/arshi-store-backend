from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import ProductSpecification


class ProductSpecificationRepository:

    @staticmethod
    async def replace_food_specs(
        db: AsyncSession,
        product_id: UUID,
        entries: list[tuple[str, str]],
    ):
        await db.execute(
            delete(ProductSpecification).where(
                ProductSpecification.product_id == product_id
            )
        )

        for spec_key, spec_value in entries:
            if not spec_value:
                continue
            db.add(
                ProductSpecification(
                    product_id=product_id,
                    spec_key=spec_key,
                    spec_value=str(spec_value),
                )
            )

        await db.commit()
