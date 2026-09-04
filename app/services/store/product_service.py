from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.product_repository import ProductRepository
from app.utils.pagination import build_pagination
from app.utils.product_serializer import (
    serialize_store_product_detail,
    serialize_store_product_list_item,
)


class ProductService:

    @staticmethod
    async def get_products(
        db: AsyncSession,
        page: int,
        page_size: int,
        search: str | None = None,
        category_id: UUID | None = None,
        category_name: str | None = None,
        is_featured: bool | None = None,
        is_bestseller: bool | None = None,
        is_new_arrival: bool | None = None,
    ):
        products, total_records = await ProductRepository.get_products(
            db=db,
            page=page,
            page_size=page_size,
            search=search,
            category_id=category_id,
            category_name=category_name,
            is_featured=is_featured,
            is_bestseller=is_bestseller,
            is_new_arrival=is_new_arrival,
        )

        response_data = [
            serialize_store_product_list_item(product)
            for product in products
        ]

        return {
            "success": True,
            "status_code": 200,
            "message": "Products fetched successfully",
            "data": response_data,
            "pagination": build_pagination(
                page=page,
                page_size=page_size,
                total_records=total_records,
            ),
        }

    @staticmethod
    async def get_product_details(
        db: AsyncSession,
        product_id: UUID,
    ):
        product = await ProductRepository.get_product_by_id(
            db=db,
            product_id=product_id,
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        return {
            "success": True,
            "status_code": 200,
            "message": "Product details fetched successfully",
            "data": serialize_store_product_detail(product),
        }
