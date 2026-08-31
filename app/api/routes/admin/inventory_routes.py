from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin

from app.schemas.admin.common_schema import ApiResponse

from app.services.admin.inventory_service import (
    InventoryService
)

router = APIRouter(
    prefix="/admin/inventory",
    tags=["Admin Inventory"]
)


@router.get(
    "",
    response_model=ApiResponse
)
async def get_inventory(
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    inventory = await InventoryService.get_inventory_dashboard(
        db
    )

    return ApiResponse(
        success=True,
        status_code=200,
        message="Inventory dashboard fetched successfully",
        data=inventory
    )