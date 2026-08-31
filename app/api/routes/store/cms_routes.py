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


@router.post("/newsletter/subscribe")
async def subscribe_newsletter(
    payload: NewsletterSubscribeRequest,
    db: AsyncSession = Depends(get_db),
):
    return await StoreCmsService.subscribe_newsletter(db, payload.email)
