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

DEFAULT_ABOUT_PAGE = {
    "hero_title": "About Arshi Naturals",
    "hero_subtitle": "Pure. Authentic. Homemade with Love.",
    "hero_button_text": "Explore Our Products",
    "story_title": "Our Story",
    "story_paragraphs": [
        "Arshi Naturals was born from a passion for preserving the authentic flavors of traditional Indian homemade foods. What started as a family kitchen sharing pickles and snacks with neighbors has grown into a beloved brand serving food lovers across India.",
        "Every jar of pickle, every batch of murukulu, and every sweet laddu is crafted with the same love and care that our grandmothers put into their cooking. We believe that food is not just nourishment — it is memory, tradition, and love.",
        "From our kitchen in Guntur, Andhra Pradesh, we bring you the finest homemade pickles, snacks, sweets, powders and natural products — all made with 100% natural ingredients and no artificial preservatives.",
    ],
    "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?w=800&q=80",
    "stats": [
        {"value": "15+", "label": "Years of Tradition"},
        {"value": "10,000+", "label": "Happy Customers"},
        {"value": "50+", "label": "Homemade Products"},
        {"value": "100%", "label": "Natural Ingredients"},
    ],
    "features_title": "Why Choose Us",
    "features": [
        {"icon_name": "Leaf", "title": "100% Natural Ingredients", "description": "Fresh, natural ingredients with no artificial preservatives or colors"},
        {"icon_name": "BadgeCheck", "title": "Traditional Recipes", "description": "Time-honored family recipes passed down through generations"},
        {"icon_name": "Zap", "title": "Freshly Prepared", "description": "Small-batch preparation for maximum freshness and authentic taste"},
    ],
    "delivery_title": "Delivering Across India",
    "delivery_locations": ["Guntur", "Vijayawada", "Hyderabad", "Bangalore", "Chennai"],
    "phone": "+91 9885161899",
    "email": "info@arshinaturals.com",
    "address": "Guntur, Andhra Pradesh 522001, India",
}

DEFAULT_CONTACT_PAGE = {
    "title": "Get in Touch",
    "description": "We'd love to hear from you. We typically respond within 2 hours during business hours.",
    "form_title": "Send Us a Message",
    "subjects": ["General Enquiry", "Product Enquiry", "Bulk Order", "Order Support"],
    "phones": ["+91 9885161899", "+91 9849845670"],
    "email": "info@arshinaturals.com",
    "address": "Guntur, Andhra Pradesh 522001, India",
    "map_embed_url": "https://maps.google.com/maps?q=Guntur%20Andhra%20Pradesh&t=&z=15&ie=UTF8&iwloc=&output=embed",
}

DEFAULT_FOOTER = {
    "tagline": "Pure. Authentic. Homemade with Love.",
    "description": "Premium homemade pickles, snacks, sweets and natural foods crafted with traditional recipes and delivered fresh to your doorstep.",
    "quick_links": [
        {"label": "Home", "href": "/"},
        {"label": "Shop", "href": "/products"},
        {"label": "Categories", "href": "/categories"},
        {"label": "About Us", "href": "/about"},
        {"label": "Contact Us", "href": "/contact"},
    ],
    "support_links": [
        {"label": "My Orders", "href": "/orders"},
        {"label": "Wishlist", "href": "/wishlist"},
        {"label": "Cart", "href": "/cart"},
        {"label": "Shipping Policy", "href": "/shipping-policy"},
        {"label": "Return Policy", "href": "/return-policy"},
    ],
    "phones": ["+91 9885161899", "+91 9849845670"],
    "email": "info@arshinaturals.com",
    "address": "Guntur, Andhra Pradesh 522001, India",
    "developer_name": "Orange Quantum Hub",
    "developer_url": "https://www.ameyait.com/",
    "copyright": "2026 Arshi Naturals. All rights reserved.",
    "payment_methods": ["Razorpay", "UPI", "PhonePe", "COD"],
}

DEFAULT_SITE_META = {
    "title": "Arshi Naturals | Pure. Authentic. Homemade with Love.",
    "description": "Premium homemade pickles, snacks, sweets and natural foods crafted with traditional recipes. Delivered fresh to your doorstep.",
    "favicon": "/logo.jpeg",
    "og_image": "/logo.jpeg",
}

DEFAULT_WHATSAPP = {
    "phone_number": "919885161899",
    "message": "Hi Arshi Naturals, I would like to know more about your products.",
    "enabled": True,
}

DEFAULT_WELCOME_POPUP = {
    "enabled": True,
    "image_url": "/welcome-banner.png",
    "redirect_url": "/products",
    "display_duration_ms": 6000,
}

DEFAULT_SOCIAL_MEDIA = {
    "facebook": "https://facebook.com",
    "instagram": "https://instagram.com",
    "youtube": "https://youtube.com",
    "twitter": "",
    "whatsapp": "919885161899",
}

DEFAULT_POLICIES = {
    "shipping_policy": "<h2>Shipping Policy</h2><p>We ship across India. Orders are processed within 1-2 business days. Delivery typically takes 3-7 business days depending on your location.</p>",
    "return_policy": "<h2>Return Policy</h2><p>We take great care in packaging our products. If you receive a damaged or wrong product, please contact us within 48 hours of delivery.</p>",
    "terms_and_conditions": "<h2>Terms & Conditions</h2><p>By using our website, you agree to these terms and conditions.</p>",
    "privacy_policy": "<h2>Privacy Policy</h2><p>Your privacy is important to us. We collect only necessary information to process your orders.</p>",
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
    async def get_about_page(db: AsyncSession):
        content = await StoreCmsService._get_content(db, "about_page", DEFAULT_ABOUT_PAGE)
        return {
            "success": True,
            "status_code": 200,
            "message": "About page data fetched successfully",
            "data": content,
        }

    @staticmethod
    async def get_contact_page(db: AsyncSession):
        content = await StoreCmsService._get_content(db, "contact_page", DEFAULT_CONTACT_PAGE)
        return {
            "success": True,
            "status_code": 200,
            "message": "Contact page data fetched successfully",
            "data": content,
        }

    @staticmethod
    async def get_footer(db: AsyncSession):
        content = await StoreCmsService._get_content(db, "footer", DEFAULT_FOOTER)
        return {
            "success": True,
            "status_code": 200,
            "message": "Footer data fetched successfully",
            "data": content,
        }

    @staticmethod
    async def get_site_meta(db: AsyncSession):
        content = await StoreCmsService._get_content(db, "site_meta", DEFAULT_SITE_META)
        return {
            "success": True,
            "status_code": 200,
            "message": "Site metadata fetched successfully",
            "data": content,
        }

    @staticmethod
    async def get_whatsapp(db: AsyncSession):
        content = await StoreCmsService._get_content(db, "whatsapp", DEFAULT_WHATSAPP)
        return {
            "success": True,
            "status_code": 200,
            "message": "WhatsApp settings fetched successfully",
            "data": content,
        }

    @staticmethod
    async def get_welcome_popup(db: AsyncSession):
        content = await StoreCmsService._get_content(db, "welcome_popup", DEFAULT_WELCOME_POPUP)
        return {
            "success": True,
            "status_code": 200,
            "message": "Welcome popup data fetched successfully",
            "data": content,
        }

    @staticmethod
    async def get_social_media(db: AsyncSession):
        content = await StoreCmsService._get_content(db, "social_media", DEFAULT_SOCIAL_MEDIA)
        return {
            "success": True,
            "status_code": 200,
            "message": "Social media data fetched successfully",
            "data": content,
        }

    @staticmethod
    async def get_policies(db: AsyncSession):
        content = await StoreCmsService._get_content(db, "policies", DEFAULT_POLICIES)
        return {
            "success": True,
            "status_code": 200,
            "message": "Policies fetched successfully",
            "data": content,
        }

    @staticmethod
    async def get_all_site_content(db: AsyncSession):
        keys = [
            "hero", "newsletter", "instagram", "about_page", "contact_page",
            "footer", "site_meta", "whatsapp", "welcome_popup", "social_media", "policies",
        ]
        defaults = {
            "hero": DEFAULT_HERO_CONTENT,
            "newsletter": DEFAULT_NEWSLETTER_CONTENT,
            "instagram": DEFAULT_INSTAGRAM_CONTENT,
            "about_page": DEFAULT_ABOUT_PAGE,
            "contact_page": DEFAULT_CONTACT_PAGE,
            "footer": DEFAULT_FOOTER,
            "site_meta": DEFAULT_SITE_META,
            "whatsapp": DEFAULT_WHATSAPP,
            "welcome_popup": DEFAULT_WELCOME_POPUP,
            "social_media": DEFAULT_SOCIAL_MEDIA,
            "policies": DEFAULT_POLICIES,
        }
        result = {}
        for key in keys:
            result[key] = await StoreCmsService._get_content(db, key, defaults[key])
        return result

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

        all_content = await StoreCmsService.get_all_site_content(db)

        return {
            "success": True,
            "status_code": 200,
            "message": "CMS content fetched successfully",
            "data": {
                **all_content,
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
