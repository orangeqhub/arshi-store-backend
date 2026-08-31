"""Shared product serialization for store & admin APIs — Arshi Naturals food fields."""

from __future__ import annotations

FOOD_SPEC_KEYS = {
    "weight",
    "ingredients",
    "shelf_life",
    "spice_level",
    "nutritional_info",
    "storage_instructions",
}


def calculate_discount(mrp, sale_price) -> int:
    if float(mrp) <= 0:
        return 0
    return round(
        ((float(mrp) - float(sale_price)) / float(mrp)) * 100
    )


def get_stock_status(stock_qty: int, food_labels: bool = False) -> str:
    if stock_qty <= 0:
        return "Out of Stock"
    if stock_qty <= 10:
        return "Limited Batch Available" if food_labels else "Limited Stock"
    return "Freshly Prepared" if food_labels else "In Stock"


def get_approved_reviews(product) -> list:
    return [
        review
        for review in (product.reviews or [])
        if review.status.value == "approved"
    ]


def compute_rating_stats(approved_reviews: list) -> tuple[float, int, dict]:
    review_count = len(approved_reviews)
    average_rating = round(
        sum(review.rating for review in approved_reviews) / review_count,
        1,
    ) if review_count > 0 else 0.0

    rating_breakdown = {
        "5_star": 0,
        "4_star": 0,
        "3_star": 0,
        "2_star": 0,
        "1_star": 0,
    }
    for review in approved_reviews:
        key = f"{review.rating}_star"
        if key in rating_breakdown:
            rating_breakdown[key] += 1

    return average_rating, review_count, rating_breakdown


def specs_to_map(specifications) -> dict[str, str]:
    result = {}
    for spec in specifications or []:
        key = (spec.spec_key or "").strip().lower().replace(" ", "_")
        if spec.spec_value:
            result[key] = spec.spec_value
    return result


def extract_food_fields(product, specifications=None) -> dict:
    spec_map = specs_to_map(
        specifications if specifications is not None else getattr(product, "specifications", [])
    )

    return {
        "weight": spec_map.get("weight") or product.sku,
        "ingredients": spec_map.get("ingredients") or product.manufacturer,
        "shelf_life": spec_map.get("shelf_life") or product.hsn_code,
        "spice_level": spec_map.get("spice_level"),
        "nutritional_info": spec_map.get("nutritional_info") or product.short_description,
        "storage_instructions": spec_map.get(
            "storage_instructions",
            "Store in a cool, dry place",
        ),
    }


def build_reviews_block(approved_reviews: list) -> list:
    average_rating, review_count, rating_breakdown = compute_rating_stats(
        approved_reviews
    )

    return [
        {
            "rating_summary": {
                "average_rating": average_rating,
                "total_reviews": review_count,
                "five_star": rating_breakdown["5_star"],
                "four_star": rating_breakdown["4_star"],
                "three_star": rating_breakdown["3_star"],
                "two_star": rating_breakdown["2_star"],
                "one_star": rating_breakdown["1_star"],
            },
            "reviews": [
                {
                    "id": str(review.id),
                    "user": {
                        "id": str(review.user.id),
                        "name": review.user.full_name,
                    },
                    "rating": review.rating,
                    "review_text": review.review_text,
                    "image_url": review.image_url,
                    "is_verified_purchase": review.is_verified_purchase,
                    "created_at": review.created_at,
                }
                for review in approved_reviews
            ],
        }
    ]


def serialize_store_product_list_item(product) -> dict:
    approved_reviews = get_approved_reviews(product)
    average_rating, review_count, _ = compute_rating_stats(approved_reviews)
    food_fields = extract_food_fields(product)

    return {
        "id": str(product.id),
        "category_id": str(product.category_id) if product.category_id else None,
        "category_name": product.category.name if product.category else None,
        "category_slug": product.category.slug if product.category else None,
        "name": product.name,
        "slug": product.slug,
        "sku": product.sku,
        "brand": product.brand,
        "short_description": product.short_description,
        "mrp": str(product.mrp),
        "sale_price": str(product.sale_price),
        "discount_percentage": calculate_discount(product.mrp, product.sale_price),
        "stock_qty": product.stock_qty,
        "stock_status": get_stock_status(product.stock_qty, food_labels=True),
        "thumbnail_url": product.thumbnail_url,
        "rating": average_rating,
        "review_count": review_count,
        "is_featured": product.is_featured,
        "is_bestseller": product.is_bestseller,
        "is_new_arrival": product.is_new_arrival,
        "created_at": product.created_at,
        **food_fields,
        "images": [
            {
                "id": str(img.id),
                "image_url": img.image_url,
                "is_primary": img.is_primary,
                "sort_order": img.sort_order,
            }
            for img in product.images
        ],
    }


def serialize_store_product_detail(product) -> dict:
    approved_reviews = get_approved_reviews(product)
    average_rating, review_count, _ = compute_rating_stats(approved_reviews)
    food_fields = extract_food_fields(product)

    return {
        "id": str(product.id),
        "category": {
            "id": str(product.category.id) if product.category else None,
            "name": product.category.name if product.category else None,
            "slug": product.category.slug if product.category else None,
        },
        "name": product.name,
        "slug": product.slug,
        "sku": product.sku,
        "brand": product.brand,
        "description": product.description,
        "short_description": product.short_description,
        "mrp": str(product.mrp),
        "sale_price": str(product.sale_price),
        "discount_percentage": calculate_discount(product.mrp, product.sale_price),
        "stock_qty": product.stock_qty,
        "stock_status": get_stock_status(product.stock_qty, food_labels=True),
        "thumbnail_url": product.thumbnail_url,
        "manufacturer": product.manufacturer,
        "hsn_code": product.hsn_code,
        "status": product.status.value,
        "rating": average_rating,
        "review_count": review_count,
        "is_featured": product.is_featured,
        "is_bestseller": product.is_bestseller,
        "is_new_arrival": product.is_new_arrival,
        **food_fields,
        "images": [
            {
                "id": str(img.id),
                "image_url": img.image_url,
                "is_primary": img.is_primary,
                "sort_order": img.sort_order,
            }
            for img in product.images
        ],
        "specifications": [
            {
                "id": str(spec.id),
                "spec_key": spec.spec_key,
                "spec_value": spec.spec_value,
            }
            for spec in product.specifications
        ],
        "reviews": build_reviews_block(approved_reviews),
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }


def default_food_spec_entries(product) -> list[tuple[str, str]]:
    entries = []
    if product.sku:
        entries.append(("weight", product.sku))
    if product.manufacturer:
        entries.append(("ingredients", product.manufacturer))
    if product.hsn_code:
        entries.append(("shelf_life", product.hsn_code))
    if product.short_description:
        entries.append(("nutritional_info", product.short_description))
    entries.append(
        ("storage_instructions", "Store in a cool, dry place")
    )
    return entries
