"""
One-off backfill: convert existing absolute product image URLs stored in the
database into portable "/uploads/products/..." paths.

Background: LocalStorage.upload_product_image() used to bake the
environment's SITE_URL into the stored URL at upload time (see
app/core/storage.py). That's now fixed for new uploads, but rows created
before the fix still hold absolute URLs like:

    http://localhost:8000/uploads/products/a.png
    https://api.arshinaturals.com/uploads/products/a.png

This script rewrites those to the portable form:

    /uploads/products/a.png

Scope (product images ONLY):
    - product_images.image_url
    - products.thumbnail_url

CMS/banner/category images (served via upload_cms_image, a different
column/table entirely) are never touched by this script.

Usage:
    python scripts/backfill_product_image_urls.py --dry-run   # preview only
    python scripts/backfill_product_image_urls.py             # apply

Safe to re-run: rows already in the portable form (or that don't reference
/uploads/products/ at all) are left untouched, so running this twice in a
row updates zero rows the second time.
"""

import argparse
import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.models import Product, ProductImage

# Matches "/uploads/products/..." anywhere in the string and captures it
# through to the end — this is the portable path we want to keep.
UPLOADS_PRODUCTS_PATTERN = re.compile(r"(/uploads/products/.+)$")


def normalize(url: str | None) -> str | None:
    """Returns the portable path if `url` needs rewriting, else None.

    None means "leave this row alone" — either it doesn't reference
    /uploads/products/ at all (rule 1: only touch those that do; CMS/banner/
    category URLs never match), or it's already in the portable form
    (idempotent: re-running the script is a no-op for already-fixed rows).
    """
    if not url:
        return None

    match = UPLOADS_PRODUCTS_PATTERN.search(url)
    if not match:
        return None

    portable = match.group(1)
    if portable == url:
        return None

    return portable


async def collect_changes(session, model, column_name: str):
    column = getattr(model, column_name)

    result = await session.execute(
        select(model.id, column).where(column.isnot(None))
    )

    changes = []
    for row_id, value in result.all():
        new_value = normalize(value)
        if new_value is not None:
            changes.append((row_id, value, new_value))

    return changes


def print_preview(label: str, changes: list, limit: int = 20):
    print(f"\n{label}: {len(changes)} row(s) to update")
    for row_id, old_value, new_value in changes[:limit]:
        print(f"  [{row_id}] {old_value!r} -> {new_value!r}")
    if len(changes) > limit:
        print(f"  ... and {len(changes) - limit} more")


async def apply_changes(session, model, column_name: str, changes: list):
    column = getattr(model, column_name)

    for row_id, _old_value, new_value in changes:
        await session.execute(
            model.__table__.update()
            .where(model.id == row_id)
            .values(**{column_name: new_value})
        )

    if changes:
        await session.commit()


async def main(dry_run: bool):
    async with AsyncSessionLocal() as session:
        product_image_changes = await collect_changes(
            session, ProductImage, "image_url"
        )
        product_thumbnail_changes = await collect_changes(
            session, Product, "thumbnail_url"
        )

        print_preview("product_images.image_url", product_image_changes)
        print_preview("products.thumbnail_url", product_thumbnail_changes)

        total = len(product_image_changes) + len(product_thumbnail_changes)
        print(f"\nTotal rows to update: {total}")

        if total == 0:
            print("Nothing to do.")
            return

        if dry_run:
            print("\nDry run — no changes written. Re-run without --dry-run to apply.")
            return

        await apply_changes(
            session, ProductImage, "image_url", product_image_changes
        )
        await apply_changes(
            session, Product, "thumbnail_url", product_thumbnail_changes
        )

        print(f"\nDone. Updated {total} row(s).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Backfill absolute product image URLs in the database to "
            "portable /uploads/products/... paths."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the changes without writing anything to the database.",
    )
    args = parser.parse_args()

    asyncio.run(main(dry_run=args.dry_run))
