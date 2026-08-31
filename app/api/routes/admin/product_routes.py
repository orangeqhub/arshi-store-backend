from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    Query,
    status
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin

from app.schemas.admin.product_schema import (
    ProductCreate,
    ProductUpdate
)

from app.services.admin.product_service import (
    ProductService
)

router = APIRouter(
    prefix="/admin/products",
    tags=["Admin Products"]
)


# =====================================================
# CREATE PRODUCT
# =====================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
async def create_product(
    category_id: UUID = Form(...),
    name: str = Form(...),
    sku: str = Form(...),
    brand: str | None = Form(None),
    description: str | None = Form(None),
    short_description: str | None = Form(None),
    mrp: float = Form(...),
    sale_price: float = Form(...),
    stock_qty: int = Form(0),
    manufacturer: str | None = Form(None),
    hsn_code: str | None = Form(None),
    is_featured: bool = Form(False),
    is_bestseller: bool = Form(False),
    is_new_arrival: bool = Form(False),
    images: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    payload = ProductCreate(
        category_id=category_id,
        name=name,
        sku=sku,
        brand=brand,
        description=description,
        short_description=short_description,
        mrp=mrp,
        sale_price=sale_price,
        stock_qty=stock_qty,
        manufacturer=manufacturer,
        hsn_code=hsn_code,
        is_featured=is_featured,
        is_bestseller=is_bestseller,
        is_new_arrival=is_new_arrival
    )

    return await ProductService.create_product(
        db=db,
        payload=payload,
        images=images
    )


# =====================================================
# GET ALL PRODUCTS
# =====================================================

@router.get("")
async def get_products(
    page: int = Query(
        1,
        ge=1
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100
    ),
    search: str | None = Query(
        None
    ),
    category_id: UUID | None = Query(
        None
    ),
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    return await ProductService.get_products(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id
    )


# =====================================================
# GET PRODUCT DETAILS
# =====================================================

@router.get("/{product_id}")
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    return await ProductService.get_product(
        db=db,
        product_id=product_id
    )


# =====================================================
# UPDATE PRODUCT
# =====================================================

@router.put("/{product_id}")
async def update_product(
    product_id: UUID,
    category_id: UUID | None = Form(None),
    name: str | None = Form(None),
    sku: str | None = Form(None),
    brand: str | None = Form(None),
    description: str | None = Form(None),
    short_description: str | None = Form(None),
    mrp: float | None = Form(None),
    sale_price: float | None = Form(None),
    stock_qty: int | None = Form(None),
    manufacturer: str | None = Form(None),
    hsn_code: str | None = Form(None),
    is_featured: bool | None = Form(None),
    is_bestseller: bool | None = Form(None),
    is_new_arrival: bool | None = Form(None),
    images: list[UploadFile] | None = File(None),
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    payload = ProductUpdate(
        category_id=category_id,
        name=name,
        sku=sku,
        brand=brand,
        description=description,
        short_description=short_description,
        mrp=mrp,
        sale_price=sale_price,
        stock_qty=stock_qty,
        manufacturer=manufacturer,
        hsn_code=hsn_code,
        is_featured=is_featured,
        is_bestseller=is_bestseller,
        is_new_arrival=is_new_arrival
    )

    return await ProductService.update_product(
        db=db,
        product_id=product_id,
        payload=payload,
        images=images
    )


# =====================================================
# DELETE PRODUCT
# =====================================================

@router.delete("/{product_id}")
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):

    return await ProductService.delete_product(
        db=db,
        product_id=product_id
    )