from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import ProductSpecification
from app.utils.product_serializer import default_food_spec_entries


async def sync_food_specifications(db: AsyncSession, product) -> None:
    """Map admin product fields into food specification rows (no schema change)."""
    existing = {
        (spec.spec_key or "").strip().lower(): spec
        for spec in (product.specifications or [])
    }

    for spec_key, spec_value in default_food_spec_entries(product):
        key = spec_key.lower()
        if key in existing:
            existing[key].spec_value = spec_value
        else:
            db.add(
                ProductSpecification(
                    product_id=product.id,
                    spec_key=spec_key,
                    spec_value=spec_value,
                )
            )

    await db.commit()

    if hasattr(product, "specifications"):
        await db.refresh(product, attribute_names=["specifications"])
