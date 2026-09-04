-- Manual migration for product weight/size variants.
--
-- This project has no Alembic migrations wired up (alembic.ini / env.py are
-- empty) — tables are provisioned via SQLAlchemy's Base.metadata.create_all
-- at app startup (see app/main.py). create_all() only CREATEs tables that
-- don't exist yet, so on next boot it will automatically create the new
-- `product_variants` table for you — but it will NOT add the new columns to
-- the already-existing `cart_items` and `order_items` tables. Run this
-- script once against the existing database (before or right after
-- deploying the new backend code) to add those columns.
--
-- Safe to run on a database that already has data: all new columns are
-- nullable, so existing products/cart items/orders are left untouched and
-- keep working exactly as before (no variant selected = legacy behaviour).

-- 1) cart_items: add variant_id, and widen the uniqueness constraint so the
--    same product can appear as separate cart lines per variant.
ALTER TABLE cart_items
    ADD COLUMN IF NOT EXISTS variant_id UUID NULL
        REFERENCES product_variants(id) ON DELETE CASCADE;

-- Drop the old (user_id, product_id) unique constraint if present.
-- The exact auto-generated name may differ; check with:
--   SELECT conname FROM pg_constraint WHERE conrelid = 'cart_items'::regclass AND contype = 'u';
ALTER TABLE cart_items
    DROP CONSTRAINT IF EXISTS cart_items_user_id_product_id_key;

ALTER TABLE cart_items
    ADD CONSTRAINT cart_items_user_id_product_id_variant_id_key
        UNIQUE (user_id, product_id, variant_id);

-- 2) order_items: add variant snapshot columns.
ALTER TABLE order_items
    ADD COLUMN IF NOT EXISTS variant_id UUID NULL
        REFERENCES product_variants(id) ON DELETE RESTRICT,
    ADD COLUMN IF NOT EXISTS variant_label VARCHAR(100) NULL,
    ADD COLUMN IF NOT EXISTS variant_sku VARCHAR(100) NULL;

-- Note: `product_variants` itself does not need to be created here —
-- Base.metadata.create_all() creates it automatically on the next app
-- startup because it's a brand-new table. Run this script AFTER that first
-- boot (so product_variants exists for the FK references above), or run
-- `python -c "..."`/restart the API once first, then run this file.
