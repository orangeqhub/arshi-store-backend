from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin

from app.schemas.admin.common_schema import ApiResponse

from app.services.admin.user_service import (
    UserService
)

router = APIRouter(
    prefix="/admin/customers",
    tags=["Admin Customers"]
)


@router.get(
    "",
    response_model=ApiResponse
)
async def get_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    customers = await UserService.get_customers(
        db,
        page,
        page_size,
        search
    )

    return ApiResponse(
        success=True,
        status_code=200,
        message="Customers fetched successfully",
        data=customers
    )


@router.get(
    "/{customer_id}",
    response_model=ApiResponse
)
async def get_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    customer = await UserService.get_customer(
        db,
        customer_id
    )

    return ApiResponse(
        success=True,
        status_code=200,
        message="Customer fetched successfully",
        data=customer
    )