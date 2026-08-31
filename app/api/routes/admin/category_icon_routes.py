from fastapi import APIRouter
from fastapi import Depends

from app.core.dependencies import (
    get_current_admin
)

from app.utils.category_master import (
    CATEGORY_MASTER
)

router = APIRouter(
    prefix="/admin/category-master",
    tags=["Admin Category Master"]
)


@router.get("")
async def get_category_master(
    admin=Depends(get_current_admin)
):

    return {
        "success": True,
        "status_code": 200,
        "message": "Category master fetched successfully",
        "data": CATEGORY_MASTER
    }