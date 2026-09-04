from uuid import UUID

from app.models.models import WishlistItem
from app.repositories.wishlist_repository import WishlistRepository
from app.repositories.product_repository import ProductRepository
from app.utils.product_serializer import (
    calculate_discount,
    get_stock_status,
)


class WishlistService:

    @staticmethod
    async def add_to_wishlist(
        db,
        user_id: UUID,
        product_id: UUID
    ):

        product = await ProductRepository.get_by_id(
            db,
            product_id
        )

        if not product:
            return {
                "success": False,
                "status_code": 404,
                "message": "Product not found"
            }

        existing = await WishlistRepository.get_by_user_and_product(
            db,
            user_id,
            product_id
        )

        if existing:
            return {
                "success": False,
                "status_code": 400,
                "message": "Product already in wishlist"
            }

        wishlist_item = WishlistItem(
            user_id=user_id,
            product_id=product_id
        )

        await WishlistRepository.create(
            db,
            wishlist_item
        )

        return {
            "success": True,
            "status_code": 201,
            "message": "Product added to wishlist"
        }

    @staticmethod
    async def get_wishlist(
        db,
        user_id: UUID,
        page: int,
        page_size: int
    ):

        items, total_records = await WishlistRepository.get_user_wishlist(
            db=db,
            user_id=user_id,
            page=page,
            page_size=page_size
        )

        total_pages = (
            (total_records + page_size - 1) // page_size
            if total_records > 0
            else 0
        )

        if not items:
            return {
                "success": True,
                "status_code": 200,
                "message": "Your wishlist is empty",
                "data": [],
                "pagination": {
                    "current_page": page,
                    "page_size": page_size,
                    "total_records": 0,
                    "total_pages": 0,
                    "has_next": False,
                    "has_previous": False
                }
            }

        wishlist_data = []

        for item in items:

            product = item.product

            discount_percentage = calculate_discount(
                product.mrp,
                product.sale_price,
            )

            stock_status = get_stock_status(
                product.stock_qty,
                food_labels=True,
            )

            wishlist_data.append(
                {
                    "wishlist_id": str(item.id),

                    "product_id": str(product.id),

                    "category_id": str(product.category_id)
                    if product.category_id
                    else None,

                    "category_name": (
                        product.category.name
                        if product.category
                        else None
                    ),

                    "name": product.name,
                    "slug": product.slug,
                    "sku": product.sku,
                    "brand": product.brand,

                    "short_description": product.short_description,

                    "mrp": str(product.mrp),
                    "sale_price": str(product.sale_price),

                    "discount_percentage": discount_percentage,

                    "stock_qty": product.stock_qty,
                    "stock_status": stock_status,

                    "thumbnail_url": product.thumbnail_url,

                    "rating": str(product.rating),
                    "review_count": product.review_count,

                    "is_featured": product.is_featured,
                    "is_bestseller": product.is_bestseller,
                    "is_new_arrival": product.is_new_arrival,

                    "created_at": product.created_at,

                    "images": [
                        {
                            "id": str(image.id),
                            "image_url": image.image_url,
                            "is_primary": image.is_primary,
                            "sort_order": image.sort_order
                        }
                        for image in product.images
                    ]
                }
            )

        return {
            "success": True,
            "status_code": 200,
            "message": "Wishlist fetched successfully",
            "data": wishlist_data,
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
    async def remove_from_wishlist(
        db,
        user_id: UUID,
        product_id: UUID
    ):

        item = await WishlistRepository.get_by_user_and_product(
            db,
            user_id,
            product_id
        )

        if not item:
            return {
                "success": False,
                "status_code": 404,
                "message": "Product not found in wishlist"
            }

        await WishlistRepository.delete(
            db,
            item
        )

        return {
            "success": True,
            "status_code": 200,
            "message": "Product removed from wishlist"
        }