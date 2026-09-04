from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.schemas.customer.address_schema import (
    AddressCreateRequest
)

from app.services.customer.address_service import (
    AddressService
)
from uuid import UUID

from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.schemas.customer.address_schema import (
    AddressCreateRequest
)

from app.services.customer.address_service import (
    AddressService
)

router = APIRouter(
    prefix="/customer/addresses",
    tags=["Customer Address"]
)

@router.post("")
async def create_address(
    payload: AddressCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return await AddressService.create_address(
        db=db,
        user_id=current_user["sub"],
        payload=payload
    )


@router.get("")
async def get_addresses(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return await AddressService.get_addresses(
        db=db,
        user_id=current_user["sub"]
    )


@router.get("/{address_id}")
async def get_address(
    address_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return await AddressService.get_address(
        db=db,
        user_id=current_user["sub"],
        address_id=address_id
    )


@router.put("/{address_id}")
async def update_address(
    address_id: UUID,
    payload: AddressCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return await AddressService.update_address(
        db=db,
        user_id=current_user["sub"],
        address_id=address_id,
        payload=payload
    )


@router.delete("/{address_id}")
async def delete_address(
    address_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return await AddressService.delete_address(
        db=db,
        user_id=current_user["sub"],
        address_id=address_id
    )