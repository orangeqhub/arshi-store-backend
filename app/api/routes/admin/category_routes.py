from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin

from app.schemas.admin.category_schema import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse
)       

from app.schemas.admin.common_schema import (
    ApiResponse
)

from app.services.admin.category_service import (
    CategoryService
)

router = APIRouter(
    prefix="/admin/categories",
    tags=["Admin Categories"]
)


@router.post(
    "",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    category = await CategoryService.create_category(
        db=db,
        name=payload.name,
        description=payload.description,
        icon=payload.icon,
        image_url=payload.image_url,
        parent_id=payload.parent_id,
        is_active=payload.is_active
    )

    return ApiResponse(
        success=True,
        status_code=201,
        message="Category created successfully",
        data=CategoryResponse.model_validate(
            category
        )
    )

@router.get(
    "",
    response_model=ApiResponse
)
async def get_categories(
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    categories = await CategoryService.get_categories(
        db
    )

    return ApiResponse(
        success=True,
        status_code=200,
        message="Categories fetched successfully",
        data=[
            CategoryResponse.model_validate(
                category
            )
            for category in categories
        ]
    )


@router.get(
    "/{category_id}",
    response_model=ApiResponse
)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    category = await CategoryService.get_category(
        db,
        category_id
    )

    return ApiResponse(
        success=True,
        status_code=200,
        message="Category fetched successfully",
        data=CategoryResponse.model_validate(
            category
        )
    )


@router.put(
    "/{category_id}",
    response_model=ApiResponse
)
async def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    category = await CategoryService.update_category(
        db,
        category_id,
        payload
    )

    return ApiResponse(
        success=True,
        status_code=200,
        message="Category updated successfully",
        data=CategoryResponse.model_validate(
            category
        )
    )

@router.delete(
    "/{category_id}",
    response_model=ApiResponse
)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    await CategoryService.delete_category(
        db,
        category_id
    )

    return ApiResponse(
        success=True,
        status_code=200,
        message="Category deleted successfully",
        data=None
    )