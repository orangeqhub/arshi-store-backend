from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Banner,
    BlogPost,
    GalleryImage,
    HomepageFeature,
    NewsletterSubscriber,
    Review,
    ReviewStatus,
    SiteContent,
)


class CmsRepository:

    # ---- Banners ----

    @staticmethod
    async def get_active_banners(db: AsyncSession):
        result = await db.execute(
            select(Banner)
            .where(
                Banner.is_deleted == False,
                Banner.is_active == True,
            )
            .order_by(Banner.sort_order.asc(), Banner.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_banners(db: AsyncSession):
        result = await db.execute(
            select(Banner)
            .where(Banner.is_deleted == False)
            .order_by(Banner.sort_order.asc(), Banner.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_banner_by_id(db: AsyncSession, banner_id: UUID):
        result = await db.execute(
            select(Banner).where(
                Banner.id == banner_id,
                Banner.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def save(db: AsyncSession, entity):
        db.add(entity)
        await db.commit()
        await db.refresh(entity)
        return entity

    @staticmethod
    async def update_entity(db: AsyncSession, entity):
        await db.commit()
        await db.refresh(entity)
        return entity

    # ---- Site content ----

    @staticmethod
    async def get_site_content(db: AsyncSession, section_key: str):
        result = await db.execute(
            select(SiteContent).where(
                SiteContent.section_key == section_key
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_site_content(db: AsyncSession):
        result = await db.execute(select(SiteContent))
        return result.scalars().all()

    # ---- Blog ----

    @staticmethod
    async def get_active_blog_posts(db: AsyncSession, limit: int = 10):
        result = await db.execute(
            select(BlogPost)
            .where(
                BlogPost.is_deleted == False,
                BlogPost.is_active == True,
            )
            .order_by(BlogPost.sort_order.asc(), BlogPost.published_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_blog_posts(db: AsyncSession):
        result = await db.execute(
            select(BlogPost)
            .where(BlogPost.is_deleted == False)
            .order_by(BlogPost.sort_order.asc(), BlogPost.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_blog_by_id(db: AsyncSession, post_id: UUID):
        result = await db.execute(
            select(BlogPost).where(
                BlogPost.id == post_id,
                BlogPost.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    # ---- Gallery ----

    @staticmethod
    async def get_active_gallery(db: AsyncSession, limit: int = 12):
        result = await db.execute(
            select(GalleryImage)
            .where(
                GalleryImage.is_deleted == False,
                GalleryImage.is_active == True,
            )
            .order_by(GalleryImage.sort_order.asc(), GalleryImage.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_gallery(db: AsyncSession):
        result = await db.execute(
            select(GalleryImage)
            .where(GalleryImage.is_deleted == False)
            .order_by(GalleryImage.sort_order.asc(), GalleryImage.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_gallery_by_id(db: AsyncSession, image_id: UUID):
        result = await db.execute(
            select(GalleryImage).where(
                GalleryImage.id == image_id,
                GalleryImage.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    # ---- Features ----

    @staticmethod
    async def get_active_features(db: AsyncSession):
        result = await db.execute(
            select(HomepageFeature)
            .where(
                HomepageFeature.is_deleted == False,
                HomepageFeature.is_active == True,
            )
            .order_by(HomepageFeature.sort_order.asc(), HomepageFeature.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_features(db: AsyncSession):
        result = await db.execute(
            select(HomepageFeature)
            .where(HomepageFeature.is_deleted == False)
            .order_by(HomepageFeature.sort_order.asc(), HomepageFeature.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_feature_by_id(db: AsyncSession, feature_id: UUID):
        result = await db.execute(
            select(HomepageFeature).where(
                HomepageFeature.id == feature_id,
                HomepageFeature.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    # ---- Newsletter ----

    @staticmethod
    async def get_subscriber_by_email(db: AsyncSession, email: str):
        result = await db.execute(
            select(NewsletterSubscriber).where(
                NewsletterSubscriber.email == email
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_subscribers(db: AsyncSession):
        result = await db.execute(
            select(NewsletterSubscriber).order_by(
                NewsletterSubscriber.created_at.desc()
            )
        )
        return result.scalars().all()

    # ---- Reviews ----

    @staticmethod
    async def get_featured_reviews(db: AsyncSession, limit: int = 8):
        from sqlalchemy.orm import joinedload
        from app.models.models import Product, User

        result = await db.execute(
            select(Review)
            .options(
                joinedload(Review.user),
                joinedload(Review.product),
            )
            .where(Review.status == ReviewStatus.APPROVED)
            .order_by(Review.created_at.desc())
            .limit(limit)
        )
        return result.unique().scalars().all()
