from uuid import UUID

from fastapi import (
    HTTPException,
    UploadFile
)
from app.repositories.product_repository import (
    ProductRepository
)
from app.repositories.product_repository import ProductRepository
from app.core.storage import local_storage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from slugify import slugify

from app.models.models import (
    Product,
    ProductImage,
    ProductVariant
)

from app.repositories.product_specification_repository import (
    ProductSpecificationRepository
)

from app.utils.product_serializer import (
    default_food_spec_entries,
    extract_food_fields,
)

from app.repositories.product_repository import (
    ProductRepository
)

from app.repositories.category_repository import (
    CategoryRepository
)

from app.repositories.product_image_repository import (
    ProductImageRepository
)

from app.repositories.product_variant_repository import (
    ProductVariantRepository
)


def _serialize_variant(variant: "ProductVariant") -> dict:

    return {
        "id": str(variant.id),
        "label": variant.label,
        "weight_grams": variant.weight_grams,
        "size_value": variant.size_value,
        "sku": variant.sku,
        "mrp": str(variant.mrp),
        "sale_price": str(variant.sale_price),
        "stock_qty": variant.stock_qty,
        "is_active": variant.is_active,
        "is_default": variant.is_default,
        "sort_order": variant.sort_order,
    }


async def _validate_variant_skus(
    db: AsyncSession,
    variants: list,
    exclude_variant_ids: set | None = None
):
    """Raises 400 if any variant SKU collides with another variant in the
    same payload, or with a variant already stored for a different product."""

    exclude_variant_ids = exclude_variant_ids or set()

    seen = set()

    for item in variants:

        if item.sku in seen:
            raise HTTPException(
                status_code=400,
                detail=f"Duplicate variant SKU '{item.sku}' in request"
            )

        seen.add(item.sku)

        existing = await ProductVariantRepository.get_by_sku(
            db,
            item.sku
        )

        if existing and str(existing.id) not in exclude_variant_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Variant SKU '{item.sku}' already exists"
            )


def _build_variant_rows(product_id, variants: list) -> list["ProductVariant"]:

    rows = []

    default_seen = False

    for index, item in enumerate(variants):

        is_default = item.is_default and not default_seen

        if is_default:
            default_seen = True

        rows.append(
            ProductVariant(
                product_id=product_id,
                label=item.label,
                weight_grams=item.weight_grams,
                size_value=item.size_value,
                sku=item.sku,
                mrp=item.mrp,
                sale_price=item.sale_price,
                stock_qty=item.stock_qty,
                is_active=item.is_active,
                is_default=is_default,
                sort_order=item.sort_order or index,
            )
        )

    # If admin didn't mark any variant as default, fall back to the first
    # active one so the store always has a variant to preselect.
    if not default_seen:
        for row in rows:
            if row.is_active:
                row.is_default = True
                break

    return rows




class ProductService:

    @staticmethod
    def get_stock_status(
        stock_qty: int
    ):

        if stock_qty <= 0:
            return "Out of Stock"

        if stock_qty <= 10:
            return "Limited Stock"

        return "In Stock"

    @staticmethod
    def calculate_discount(
        mrp,
        sale_price
    ):

        if float(mrp) <= 0:
            return 0

        return round(
            (
                (
                    float(mrp)
                    - float(sale_price)
                )
                / float(mrp)
            ) * 100
        )


    @staticmethod
    async def create_product(
        db: AsyncSession,
        payload,
        images: list[UploadFile]
    ):
        try:

            category = await CategoryRepository.get_by_id(
                db,
                payload.category_id
            )

            if not category:
                raise HTTPException(
                    status_code=404,
                    detail="Category not found"
                )

            existing_sku = await ProductRepository.get_by_sku(
                db,
                payload.sku
            )

            if existing_sku:
                raise HTTPException(
                    status_code=400,
                    detail="SKU already exists"
                )

            if payload.sale_price > payload.mrp:
                raise HTTPException(
                    status_code=400,
                    detail="Sale price cannot be greater than MRP"
                )

            for variant in payload.variants:
                if variant.sale_price > variant.mrp:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Variant '{variant.label}': sale price cannot be greater than MRP"
                    )

            await _validate_variant_skus(db, payload.variants)

            if len(images) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="At least one image required"
                )

            if len(images) > 6:
                raise HTTPException(
                    status_code=400,
                    detail="Maximum 6 images allowed"
                )

            MAX_IMAGE_SIZE = 3 * 1024 * 1024

            for image in images:

                if image.content_type not in [
                    "image/jpeg",
                    "image/jpg",
                    "image/png",
                    "image/webp",
                    "image/jfif"
                ]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"{image.filename} is not a valid image"
                    )

                contents = await image.read()

                if len(contents) > MAX_IMAGE_SIZE:
                    raise HTTPException(
                        status_code=400,
                        detail=f"{image.filename} exceeds 3 MB limit"
                    )

                await image.seek(0)

            slug = slugify(payload.name)

            product = Product(
                category_id=payload.category_id,
                name=payload.name,
                slug=slug,
                sku=payload.sku,
                brand=payload.brand,
                description=payload.description,
                short_description=payload.short_description,
                mrp=payload.mrp,
                sale_price=payload.sale_price,
                stock_qty=payload.stock_qty,
                manufacturer=payload.manufacturer,
                hsn_code=payload.hsn_code,
                is_featured=payload.is_featured,
                is_bestseller=payload.is_bestseller,
                is_new_arrival=payload.is_new_arrival
            )

            product = await ProductRepository.create(
                db,
                product
            )

            image_records = []
            thumbnail_url = None

            for index, image in enumerate(images):

                image_url = await local_storage.upload_product_image(
                    image
                )

                if index == 0:
                    thumbnail_url = image_url

                image_records.append(
                    ProductImage(
                        product_id=product.id,
                        image_url=image_url,
                        is_primary=(index == 0),
                        sort_order=index
                    )
                )

            await ProductImageRepository.bulk_create(
                db,
                image_records
            )

            if payload.variants:

                variant_rows = _build_variant_rows(
                    product.id,
                    payload.variants
                )

                await ProductVariantRepository.bulk_create(
                    db,
                    variant_rows
                )

            product.thumbnail_url = thumbnail_url

            await ProductRepository.update(
                db,
                product
            )

            await ProductSpecificationRepository.replace_food_specs(
                db,
                product.id,
                default_food_spec_entries(product),
            )

            return {
                "success": True,
                "status_code": 201,
                "message": "Product created successfully",
                "data": {
                    "id": str(product.id),
                    "name": product.name,
                    "sku": product.sku
                }
            }

        except HTTPException:
            raise

        except IntegrityError:
            await db.rollback()

            raise HTTPException(
                status_code=400,
                detail="Duplicate product data found"
            )

        except Exception as e:

            await db.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Failed to create product: {str(e)}"
            )
    @staticmethod
    async def get_products(
        db: AsyncSession,
        page: int,
        page_size: int,
        search: str | None = None,
        category_id: UUID | None = None
    ):

        products, total_records = (
            await ProductRepository.get_products(
                db=db,
                page=page,
                page_size=page_size,
                search=search,
                category_id=category_id,
                active_only=False,
            )
        )

        total_pages = (
            (total_records + page_size - 1)
            // page_size
        ) if total_records else 0

        data = []

        for product in products:

            if product.stock_qty <= 0:
                stock_status = "Out of Stock"
            elif product.stock_qty <= 10:
                stock_status = "Limited Stock"
            else:
                stock_status = "In Stock"

            discount_percentage = 0

            if (
                product.mrp
                and product.sale_price
                and float(product.mrp) > 0
            ):
                discount_percentage = round(
                    (
                        (
                            float(product.mrp)
                            - float(product.sale_price)
                        )
                        / float(product.mrp)
                    ) * 100
                )

            data.append(
                {
                    "id": str(product.id),

                    "category_id": (
                        str(product.category_id)
                        if product.category_id
                        else None
                    ),

                    "category_name": (
                        product.category.name
                        if product.category
                        else None
                    ),

                    "name": product.name,
                    "slug": product.slug,
                    "sku": product.sku,
                    "brand": product.brand,

                    "short_description":
                    product.short_description,

                    "mrp": str(product.mrp),

                    "sale_price": str(
                        product.sale_price
                    ),

                    "discount_percentage":
                    discount_percentage,

                    "stock_qty":
                    product.stock_qty,

                    "stock_status":
                    stock_status,

                    "thumbnail_url":
                    product.thumbnail_url,

                    "rating": float(product.rating or 0),
                    "review_count": product.review_count or 0,


                    "is_featured":
                    product.is_featured,

                    "is_bestseller":
                    product.is_bestseller,

                    "is_new_arrival":
                    product.is_new_arrival,

                    "created_at":
                    product.created_at,

                    "images": [
                        {
                            "id": str(img.id),
                            "image_url": img.image_url,
                            "is_primary": img.is_primary,
                            "sort_order": img.sort_order
                        }
                        for img in product.images
                    ],

                    "variants": [
                        _serialize_variant(variant)
                        for variant in product.variants
                    ]
                }
            )

        return {
            "success": True,
            "status_code": 200,
            "message": "Products fetched successfully",

            "filters": {
                "search": search,
                "category_id": (
                    str(category_id)
                    if category_id
                    else None
                )
            },

            "data": data,

            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        }

    @staticmethod
    async def get_product(
        db: AsyncSession,
        product_id: UUID
    ):

        product = await ProductRepository.get_product_by_id(
            db,
            product_id
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        food_fields = extract_food_fields(product)

        return {
            "success": True,
            "status_code": 200,
            "message": "Product fetched successfully",
            "data": {
                "id": str(product.id),

                "category_id": (
                    str(product.category_id)
                    if product.category_id
                    else None
                ),

                "category_name": (
                    product.category.name
                    if product.category
                    else None
                ),

                "name": product.name,
                "slug": product.slug,
                "sku": product.sku,

                "brand": product.brand,

                "description":
                product.description,

                "short_description":
                product.short_description,

                "mrp": str(product.mrp),

                "sale_price": str(
                    product.sale_price
                ),

                "discount_percentage":
                ProductService.calculate_discount(
                    product.mrp,
                    product.sale_price
                ),

                "stock_qty":
                product.stock_qty,

                "stock_status":
                ProductService.get_stock_status(
                    product.stock_qty
                ),

                "thumbnail_url":
                product.thumbnail_url,

                "manufacturer":
                product.manufacturer,

                "hsn_code":
                product.hsn_code,

                "rating": float(product.rating or 0),
                "review_count": product.review_count or 0,

                "is_featured":
                product.is_featured,

                "is_bestseller":
                product.is_bestseller,

                "is_new_arrival":
                product.is_new_arrival,

                **food_fields,

                "specifications": [
                    {
                        "id": str(spec.id),
                        "spec_key": spec.spec_key,
                        "spec_value": spec.spec_value,
                    }
                    for spec in product.specifications
                ],

                "created_at":
                product.created_at,

                "images": [
                    {
                        "id": str(img.id),
                        "image_url": img.image_url,
                        "is_primary": img.is_primary,
                        "sort_order": img.sort_order
                    }
                    for img in product.images
                ],

                "variants": [
                    _serialize_variant(variant)
                    for variant in product.variants
                ]
            }
        }

    @staticmethod
    async def update_product(
        db: AsyncSession,
        product_id: UUID,
        payload,
        images: list[UploadFile] | None = None
    ):
        try:

            product = await ProductRepository.get_by_id(
                db,
                product_id
            )

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail="Product not found"
                )

            update_data = payload.model_dump(
                exclude_unset=True
            )

            update_data.pop("variants", None)

            if (
                "mrp" in update_data
                and "sale_price" in update_data
                and update_data["sale_price"] > update_data["mrp"]
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Sale price cannot be greater than MRP"
                )

            if payload.variants is not None:

                for variant in payload.variants:
                    if variant.sale_price > variant.mrp:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Variant '{variant.label}': sale price cannot be greater than MRP"
                        )

                existing_variants = {
                    str(v.id): v
                    for v in await ProductVariantRepository.get_by_product(
                        db,
                        product.id
                    )
                }

                submitted_ids = {
                    str(item.id)
                    for item in payload.variants
                    if item.id
                }

                await _validate_variant_skus(
                    db,
                    payload.variants,
                    exclude_variant_ids=set(existing_variants.keys())
                )

                # Delete variants that were removed from the form
                for variant_id, variant in existing_variants.items():
                    if variant_id not in submitted_ids:
                        await ProductVariantRepository.delete(db, variant)

                default_seen = False
                new_rows = []

                for index, item in enumerate(payload.variants):

                    is_default = item.is_default and not default_seen

                    if item.id and str(item.id) in existing_variants:

                        variant = existing_variants[str(item.id)]
                        variant.label = item.label
                        variant.weight_grams = item.weight_grams
                        variant.size_value = item.size_value
                        variant.sku = item.sku
                        variant.mrp = item.mrp
                        variant.sale_price = item.sale_price
                        variant.stock_qty = item.stock_qty
                        variant.is_active = item.is_active
                        variant.is_default = is_default
                        variant.sort_order = item.sort_order or index

                    else:

                        new_rows.append(
                            ProductVariant(
                                product_id=product.id,
                                label=item.label,
                                weight_grams=item.weight_grams,
                                size_value=item.size_value,
                                sku=item.sku,
                                mrp=item.mrp,
                                sale_price=item.sale_price,
                                stock_qty=item.stock_qty,
                                is_active=item.is_active,
                                is_default=is_default,
                                sort_order=item.sort_order or index,
                            )
                        )

                    if is_default:
                        default_seen = True

                if new_rows:
                    await ProductVariantRepository.bulk_create(db, new_rows)

                if not default_seen:
                    for variant in list(existing_variants.values()) + new_rows:
                        if variant.is_active:
                            variant.is_default = True
                            break

            if "name" in update_data:

                product.name = update_data["name"]

                product.slug = slugify(
                    update_data["name"]
                )

            for key, value in update_data.items():

                setattr(
                    product,
                    key,
                    value
                )

            if images:

                if len(images) > 6:
                    raise HTTPException(
                        status_code=400,
                        detail="Maximum 6 images allowed"
                    )

                MAX_IMAGE_SIZE = 3 * 1024 * 1024

                for image in images:

                    if image.content_type not in [
                        "image/jpeg",
                        "image/jpg",
                        "image/png",
                        "image/webp",
                        "image/jfif"    
                    ]:
                        raise HTTPException(
                            status_code=400,
                            detail=f"{image.filename} is not a valid image"
                        )

                    contents = await image.read()

                    if len(contents) > MAX_IMAGE_SIZE:
                        raise HTTPException(
                            status_code=400,
                            detail=f"{image.filename} exceeds 3 MB limit"
                        )

                    await image.seek(0)

                await ProductImageRepository.delete_product_images(
                    db,
                    product.id
                )

                image_records = []

                thumbnail_url = None

                for index, image in enumerate(images):

                    image_url = await local_storage.upload_product_image(
                        image
                    )

                    if index == 0:
                        thumbnail_url = image_url

                    image_records.append(
                        ProductImage(
                            product_id=product.id,
                            image_url=image_url,
                            is_primary=(index == 0),
                            sort_order=index
                        )
                    )

                await ProductImageRepository.bulk_create(
                    db,
                    image_records
                )

                product.thumbnail_url = thumbnail_url

            await ProductRepository.update(
                db,
                product
            )

            await ProductSpecificationRepository.replace_food_specs(
                db,
                product.id,
                default_food_spec_entries(product),
            )

            return {
                "success": True,
                "status_code": 200,
                "message": "Product updated successfully"
            }

        except HTTPException:
            raise

        except IntegrityError:
            await db.rollback()

            raise HTTPException(
                status_code=400,
                detail="Duplicate product data found"
            )

        except Exception as e:

            await db.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Failed to update product: {str(e)}"
            )

    @staticmethod
    async def delete_product(
        db: AsyncSession,
        product_id: UUID
    ):

        product = await ProductRepository.get_by_id(
            db,
            product_id
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        await ProductRepository.delete(
            db,
            product
        )

        return {
            "success": True,
            "status_code": 200,
            "message": "Product deleted successfully"
        }