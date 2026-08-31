from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import local_storage
from app.models.models import (
    Banner,
    BlogPost,
    GalleryImage,
    HomepageFeature,
    NewsletterSubscriber,
    SiteContent,
)
from app.repositories.cms_repository import CmsRepository
from app.repositories.product_repository import ProductRepository
from app.services.store.category_service import CategoryService
from app.utils.product_serializer import serialize_store_product_list_item


DEFAULT_HERO_CONTENT = {
    "badge": "Pure. Authentic. Homemade with Love.",
    "title": "Traditional Flavors",
    "title_highlight": "Crafted with Love",
    "description": (
        "Authentic homemade pickles, snacks, sweets and natural foods "
        "delivered fresh to your doorstep."
    ),
    "rating": 4.9,
    "customer_count": "2,400+",
    "feature_pills": [
        {"label": "100% Natural"},
        {"label": "No Artificial Preservatives"},
        {"label": "Traditional Recipes"},
        {"label": "Freshly Prepared"},
    ],
    "trust_bar": [
        {"label": "Made with Love"},
        {"label": "Hygienically Packed"},
        {"label": "Delivered with Care"},
        {"label": "Secure Payments"},
    ],
}

DEFAULT_NEWSLETTER_CONTENT = {
    "title": "Subscribe to Our Newsletter",
    "description": (
        "Get exclusive offers, new product launches and traditional recipes "
        "delivered to your inbox"
    ),
}

DEFAULT_INSTAGRAM_CONTENT = {
    "title": "From Our Kitchen",
    "description": "Follow us on Instagram for recipes, behind-the-scenes & more",
    "handle": "@arshinaturals",
    "profile_url": "https://instagram.com",
}


def _serialize_banner(banner: Banner) -> dict:
    return {
        "id": str(banner.id),
        "title": banner.title,
        "subtitle": banner.subtitle,
        "image_url": banner.image_url,
        "mobile_image_url": banner.mobile_image_url,
        "redirect_url": banner.redirect_url,
        "sort_order": banner.sort_order,
        "is_active": banner.is_active,
    }


def _serialize_blog(post: BlogPost) -> dict:
    return {
        "id": str(post.id),
        "title": post.title,
        "excerpt": post.excerpt,
        "content": post.content,
        "category": post.category,
        "image_url": post.image_url,
        "published_at": post.published_at,
        "sort_order": post.sort_order,
        "is_active": post.is_active,
    }


def _serialize_gallery(image: GalleryImage) -> dict:
    return {
        "id": str(image.id),
        "image_url": image.image_url,
        "alt_text": image.alt_text,
        "link_url": image.link_url,
        "sort_order": image.sort_order,
        "is_active": image.is_active,
    }


def _serialize_feature(feature: HomepageFeature) -> dict:
    return {
        "id": str(feature.id),
        "title": feature.title,
        "description": feature.description,
        "icon_name": feature.icon_name,
        "color": feature.color,
        "sort_order": feature.sort_order,
        "is_active": feature.is_active,
    }


class StoreCmsService:

    @staticmethod
    async def _get_content(db: AsyncSession, key: str, default: dict) -> dict:
        row = await CmsRepository.get_site_content(db, key)
        if row and row.content:
            return {**default, **row.content}
        return default

    @staticmethod
    async def get_homepage(db: AsyncSession):
        banners = await CmsRepository.get_active_banners(db)
        hero_content = await StoreCmsService._get_content(
            db, "hero", DEFAULT_HERO_CONTENT
        )
        newsletter = await StoreCmsService._get_content(
            db, "newsletter", DEFAULT_NEWSLETTER_CONTENT
        )
        instagram = await StoreCmsService._get_content(
            db, "instagram", DEFAULT_INSTAGRAM_CONTENT
        )

        featured_products, _ = await ProductRepository.get_products(
            db=db,
            page=1,
            page_size=8,
            is_featured=True,
        )
        bestsellers, _ = await ProductRepository.get_products(
            db=db,
            page=1,
            page_size=8,
            is_bestseller=True,
        )
        new_arrivals, _ = await ProductRepository.get_products(
            db=db,
            page=1,
            page_size=8,
            is_new_arrival=True,
        )

        combo_products, _ = await ProductRepository.get_products(
            db=db,
            page=1,
            page_size=6,
            category_name="Combo",
        )

        categories_response = await CategoryService.get_categories(db)
        blog_posts = await CmsRepository.get_active_blog_posts(db, limit=6)
        gallery = await CmsRepository.get_active_gallery(db, limit=12)
        features = await CmsRepository.get_active_features(db)
        reviews = await CmsRepository.get_featured_reviews(db, limit=8)

        return {
            "success": True,
            "status_code": 200,
            "message": "Homepage data fetched successfully",
            "data": {
                "banners": [_serialize_banner(b) for b in banners],
                "hero": hero_content,
                "newsletter": newsletter,
                "instagram": instagram,
                "featured_products": [
                    serialize_store_product_list_item(p)
                    for p in featured_products
                ],
                "bestsellers": [
                    serialize_store_product_list_item(p)
                    for p in bestsellers
                ],
                "new_arrivals": [
                    serialize_store_product_list_item(p)
                    for p in new_arrivals
                ],
                "combo_products": [
                    serialize_store_product_list_item(p)
                    for p in combo_products
                ],
                "categories": categories_response["data"],
                "blog_posts": [_serialize_blog(p) for p in blog_posts],
                "gallery": [_serialize_gallery(g) for g in gallery],
                "features": [_serialize_feature(f) for f in features],
                "reviews": [
                    {
                        "id": str(review.id),
                        "name": review.user.full_name if review.user else "Customer",
                        "rating": review.rating,
                        "text": review.review_text,
                        "product": review.product.name if review.product else None,
                        "created_at": review.created_at,
                    }
                    for review in reviews
                ],
            },
        }

    @staticmethod
    async def subscribe_newsletter(db: AsyncSession, email: str):
        existing = await CmsRepository.get_subscriber_by_email(db, email)
        if existing:
            return {
                "success": True,
                "status_code": 200,
                "message": "Already subscribed",
                "data": None,
            }

        subscriber = NewsletterSubscriber(email=email.lower().strip())
        await CmsRepository.save(db, subscriber)

        return {
            "success": True,
            "status_code": 201,
            "message": "Subscribed successfully",
            "data": {"email": subscriber.email},
        }


class AdminCmsService:

    @staticmethod
    async def get_all_content(db: AsyncSession):
        site_rows = await CmsRepository.get_all_site_content(db)
        site_map = {row.section_key: row.content for row in site_rows}

        return {
            "success": True,
            "status_code": 200,
            "message": "CMS content fetched successfully",
            "data": {
                "hero": site_map.get("hero", DEFAULT_HERO_CONTENT),
                "newsletter": site_map.get("newsletter", DEFAULT_NEWSLETTER_CONTENT),
                "instagram": site_map.get("instagram", DEFAULT_INSTAGRAM_CONTENT),
                "banners": [
                    _serialize_banner(b)
                    for b in await CmsRepository.get_all_banners(db)
                ],
                "blog_posts": [
                    _serialize_blog(p)
                    for p in await CmsRepository.get_all_blog_posts(db)
                ],
                "gallery": [
                    _serialize_gallery(g)
                    for g in await CmsRepository.get_all_gallery(db)
                ],
                "features": [
                    _serialize_feature(f)
                    for f in await CmsRepository.get_all_features(db)
                ],
                "subscribers": [
                    {
                        "id": str(s.id),
                        "email": s.email,
                        "created_at": s.created_at,
                    }
                    for s in await CmsRepository.get_all_subscribers(db)
                ],
            },
        }

    @staticmethod
    async def upsert_site_content(
        db: AsyncSession,
        section_key: str,
        content: dict,
    ):
        row = await CmsRepository.get_site_content(db, section_key)
        if row:
            row.content = content
            await CmsRepository.update_entity(db, row)
        else:
            row = SiteContent(section_key=section_key, content=content)
            await CmsRepository.save(db, row)

        return {
            "success": True,
            "status_code": 200,
            "message": f"{section_key} content saved",
            "data": row.content,
        }

    @staticmethod
    async def upload_image(file: UploadFile) -> str:
        allowed = {
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/webp",
        }
        if file.content_type not in allowed:
            raise HTTPException(status_code=400, detail="Invalid image type")
        return await local_storage.upload_cms_image(file)

    @staticmethod
    async def create_banner(db: AsyncSession, payload):
        banner = Banner(**payload.model_dump())
        banner = await CmsRepository.save(db, banner)
        return {
            "success": True,
            "status_code": 201,
            "message": "Banner created",
            "data": _serialize_banner(banner),
        }

    @staticmethod
    async def update_banner(db: AsyncSession, banner_id: UUID, payload):
        banner = await CmsRepository.get_banner_by_id(db, banner_id)
        if not banner:
            raise HTTPException(status_code=404, detail="Banner not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(banner, key, value)
        banner = await CmsRepository.update_entity(db, banner)
        return {
            "success": True,
            "status_code": 200,
            "message": "Banner updated",
            "data": _serialize_banner(banner),
        }

    @staticmethod
    async def delete_banner(db: AsyncSession, banner_id: UUID):
        banner = await CmsRepository.get_banner_by_id(db, banner_id)
        if not banner:
            raise HTTPException(status_code=404, detail="Banner not found")
        banner.is_deleted = True
        await CmsRepository.update_entity(db, banner)
        return {"success": True, "status_code": 200, "message": "Banner deleted"}

    @staticmethod
    async def create_blog(db: AsyncSession, payload):
        data = payload.model_dump()
        if not data.get("published_at"):
            data["published_at"] = datetime.now(timezone.utc)
        post = BlogPost(**data)
        post = await CmsRepository.save(db, post)
        return {
            "success": True,
            "status_code": 201,
            "message": "Blog post created",
            "data": _serialize_blog(post),
        }

    @staticmethod
    async def update_blog(db: AsyncSession, post_id: UUID, payload):
        post = await CmsRepository.get_blog_by_id(db, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(post, key, value)
        post = await CmsRepository.update_entity(db, post)
        return {
            "success": True,
            "status_code": 200,
            "message": "Blog post updated",
            "data": _serialize_blog(post),
        }

    @staticmethod
    async def delete_blog(db: AsyncSession, post_id: UUID):
        post = await CmsRepository.get_blog_by_id(db, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        post.is_deleted = True
        await CmsRepository.update_entity(db, post)
        return {"success": True, "status_code": 200, "message": "Blog post deleted"}

    @staticmethod
    async def create_gallery(db: AsyncSession, payload):
        image = GalleryImage(**payload.model_dump())
        image = await CmsRepository.save(db, image)
        return {
            "success": True,
            "status_code": 201,
            "message": "Gallery image created",
            "data": _serialize_gallery(image),
        }

    @staticmethod
    async def update_gallery(db: AsyncSession, image_id: UUID, payload):
        image = await CmsRepository.get_gallery_by_id(db, image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Gallery image not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(image, key, value)
        image = await CmsRepository.update_entity(db, image)
        return {
            "success": True,
            "status_code": 200,
            "message": "Gallery image updated",
            "data": _serialize_gallery(image),
        }

    @staticmethod
    async def delete_gallery(db: AsyncSession, image_id: UUID):
        image = await CmsRepository.get_gallery_by_id(db, image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Gallery image not found")
        image.is_deleted = True
        await CmsRepository.update_entity(db, image)
        return {"success": True, "status_code": 200, "message": "Gallery image deleted"}

    @staticmethod
    async def create_feature(db: AsyncSession, payload):
        feature = HomepageFeature(**payload.model_dump())
        feature = await CmsRepository.save(db, feature)
        return {
            "success": True,
            "status_code": 201,
            "message": "Feature created",
            "data": _serialize_feature(feature),
        }

    @staticmethod
    async def update_feature(db: AsyncSession, feature_id: UUID, payload):
        feature = await CmsRepository.get_feature_by_id(db, feature_id)
        if not feature:
            raise HTTPException(status_code=404, detail="Feature not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(feature, key, value)
        feature = await CmsRepository.update_entity(db, feature)
        return {
            "success": True,
            "status_code": 200,
            "message": "Feature updated",
            "data": _serialize_feature(feature),
        }

    @staticmethod
    async def delete_feature(db: AsyncSession, feature_id: UUID):
        feature = await CmsRepository.get_feature_by_id(db, feature_id)
        if not feature:
            raise HTTPException(status_code=404, detail="Feature not found")
        feature.is_deleted = True
        await CmsRepository.update_entity(db, feature)
        return {"success": True, "status_code": 200, "message": "Feature deleted"}
