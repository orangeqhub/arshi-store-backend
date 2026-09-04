from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin

from app.schemas.admin.common_schema import ApiResponse

from app.services.admin.dashboard_service import (
    DashboardService
)

router = APIRouter(
    prefix="/admin/dashboard",
    tags=["Admin Dashboard"]
)


@router.get(
    "",
    response_model=ApiResponse
)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    dashboard = await DashboardService.get_dashboard(
        db
    )

    return ApiResponse(
        success=True,
        status_code=200,
        message="Dashboard fetched successfully",
        data=dashboard
    )