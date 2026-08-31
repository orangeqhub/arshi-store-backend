from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.schemas.cms_schema import (
    BannerCreate,
    BannerUpdate,
    BlogPostCreate,
    BlogPostUpdate,
    GalleryImageCreate,
    GalleryImageUpdate,
    HomepageFeatureCreate,
    HomepageFeatureUpdate,
    SiteContentUpdate,
)
from app.services.cms_service import AdminCmsService

router = APIRouter(
    prefix="/admin/cms",
    tags=["Admin CMS"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("")
async def get_cms_content(db: AsyncSession = Depends(get_db)):
    return await AdminCmsService.get_all_content(db)


@router.put("/site/{section_key}")
async def update_site_content(
    section_key: str,
    payload: SiteContentUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await AdminCmsService.upsert_site_content(
        db, section_key, payload.content
    )


@router.post("/upload")
async def upload_cms_image(
    image: UploadFile = File(...),
):
    url = await AdminCmsService.upload_image(image)
    return {
        "success": True,
        "status_code": 200,
        "message": "Image uploaded",
        "data": {"url": url},
    }


@router.post("/banners")
async def create_banner(
    payload: BannerCreate,
    db: AsyncSession = Depends(get_db),
):
    return await AdminCmsService.create_banner(db, payload)


@router.put("/banners/{banner_id}")
async def update_banner(
    banner_id: UUID,
    payload: BannerUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await AdminCmsService.update_banner(db, banner_id, payload)


@router.delete("/banners/{banner_id}")
async def delete_banner(
    banner_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await AdminCmsService.delete_banner(db, banner_id)


@router.post("/blog")
async def create_blog(
    payload: BlogPostCreate,
    db: AsyncSession = Depends(get_db),
):
    return await AdminCmsService.create_blog(db, payload)


@router.put("/blog/{post_id}")
async def update_blog(
    post_id: UUID,
    payload: BlogPostUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await AdminCmsService.update_blog(db, post_id, payload)


@router.delete("/blog/{post_id}")
async def delete_blog(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await AdminCmsService.delete_blog(db, post_id)


@router.post("/gallery")
async def create_gallery(
    payload: GalleryImageCreate,
    db: AsyncSession = Depends(get_db),
):
    return await AdminCmsService.create_gallery(db, payload)


@router.put("/gallery/{image_id}")
async def update_gallery(
    image_id: UUID,
    payload: GalleryImageUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await AdminCmsService.update_gallery(db, image_id, payload)


@router.delete("/gallery/{image_id}")
async def delete_gallery(
    image_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await AdminCmsService.delete_gallery(db, image_id)


@router.post("/features")
async def create_feature(
    payload: HomepageFeatureCreate,
    db: AsyncSession = Depends(get_db),
):
    return await AdminCmsService.create_feature(db, payload)


@router.put("/features/{feature_id}")
async def update_feature(
    feature_id: UUID,
    payload: HomepageFeatureUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await AdminCmsService.update_feature(db, feature_id, payload)


@router.delete("/features/{feature_id}")
async def delete_feature(
    feature_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await AdminCmsService.delete_feature(db, feature_id)
