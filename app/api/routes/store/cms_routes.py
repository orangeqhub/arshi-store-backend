from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.cms_schema import NewsletterSubscribeRequest
from app.services.cms_service import StoreCmsService

router = APIRouter(
    prefix="/store/cms",
    tags=["Store CMS"],
)


@router.get("/homepage")
async def get_homepage(db: AsyncSession = Depends(get_db)):
    return await StoreCmsService.get_homepage(db)


@router.get("/about")
async def get_about_page(db: AsyncSession = Depends(get_db)):
    return await StoreCmsService.get_about_page(db)


@router.get("/contact")
async def get_contact_page(db: AsyncSession = Depends(get_db)):
    return await StoreCmsService.get_contact_page(db)


@router.get("/footer")
async def get_footer(db: AsyncSession = Depends(get_db)):
    return await StoreCmsService.get_footer(db)


@router.get("/site-meta")
async def get_site_meta(db: AsyncSession = Depends(get_db)):
    return await StoreCmsService.get_site_meta(db)


@router.get("/whatsapp")
async def get_whatsapp(db: AsyncSession = Depends(get_db)):
    return await StoreCmsService.get_whatsapp(db)


@router.get("/welcome-popup")
async def get_welcome_popup(db: AsyncSession = Depends(get_db)):
    return await StoreCmsService.get_welcome_popup(db)


@router.get("/social-media")
async def get_social_media(db: AsyncSession = Depends(get_db)):
    return await StoreCmsService.get_social_media(db)


@router.get("/policies")
async def get_policies(db: AsyncSession = Depends(get_db)):
    return await StoreCmsService.get_policies(db)


@router.post("/newsletter/subscribe")
async def subscribe_newsletter(
    payload: NewsletterSubscribeRequest,
    db: AsyncSession = Depends(get_db),
):
    return await StoreCmsService.subscribe_newsletter(db, payload.email)
