from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin

from app.schemas.admin.common_schema import ApiResponse

from app.services.admin.setting_service import (
    SettingService
)

from app.schemas.admin.setting_schema import (
    UpdateGeneralSettingsRequest,
    UpdateStoreSettingsRequest,
    UpdateDeliverySettingsRequest
)

router = APIRouter(
    prefix="/admin/settings",
    tags=["Admin Settings"]
)


@router.get(
    "/general",
    response_model=ApiResponse
)
async def get_general_settings(
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    settings = await SettingService.get_general_settings(
        db
    )

    return ApiResponse(
        success=True,
        status_code=200,
        message="General settings fetched successfully",
        data=settings
    )


@router.patch(
    "/general",
    response_model=ApiResponse
)
async def update_general_settings(
    request: UpdateGeneralSettingsRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    await SettingService.update_general_settings(
        db,
        request
    )

    return ApiResponse(
        success=True,
        status_code=200,
        message="General settings updated successfully",
        data=None
    )


@router.get(
    "/store",
    response_model=ApiResponse
)
async def get_store_settings(
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    settings = await SettingService.get_store_settings(
        db
    )

    return ApiResponse(
        success=True,
        status_code=200,
        message="Store settings fetched successfully",
        data=settings
    )


@router.patch(
    "/store",
    response_model=ApiResponse
)
async def update_store_settings(
    request: UpdateStoreSettingsRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    await SettingService.update_store_settings(
        db,
        request
    )

    return ApiResponse(
        success=True,
        status_code=200,
        message="Store settings updated successfully",
        data=None
    )


@router.get(
    "/delivery",
    response_model=ApiResponse
)
async def get_delivery_settings(
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    settings = await SettingService.get_delivery_settings(
        db
    )

    return ApiResponse(
        success=True,
        status_code=200,
        message="Delivery settings fetched successfully",
        data=settings
    )


@router.patch(
    "/delivery",
    response_model=ApiResponse
)
async def update_delivery_settings(
    request: UpdateDeliverySettingsRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    await SettingService.update_delivery_settings(
        db,
        request
    )

    return ApiResponse(
        success=True,
        status_code=200,
        message="Delivery settings updated successfully",
        data=None
    )