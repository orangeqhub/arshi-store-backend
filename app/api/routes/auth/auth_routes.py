from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from app.models.models import UserRole
from app.db.session import get_db

from app.schemas.auth_schema import (
    AdminRegisterRequest,
    UserRegisterRequest,
    LoginRequest
)

from app.services.auth_service import (
    AuthService
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

service = AuthService()


@router.post("/admin/register")
async def admin_register(
    payload: AdminRegisterRequest,
    db=Depends(get_db)
):

    user = await service.register_admin(
        db,
        payload
    )

    return {
        "success": True,
        "status_code": 201,
        "message": "Admin registered successfully",
        "data": {
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role.value,
            "created_at": user.created_at
        }
    }


@router.post("/register")
async def user_register(
    payload: UserRegisterRequest,
    db=Depends(get_db)
):

    user = await service.register_user(
        db,
        payload
    )

    return {
        "success": True,
        "status_code": 201,
        "message": "User registered successfully",
        "data": {
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role.value,
            "created_at": user.created_at
        }
    }


@router.post("/admin/login")
async def admin_login(
    payload: LoginRequest,
    db=Depends(get_db)
):

    response = await service.login(
        db,
        payload,
        UserRole.ADMIN
    )

    if response["data"]["user"]["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Not Admin"
        )

    return response


@router.post("/login")
async def user_login(
    payload: LoginRequest,
    db=Depends(get_db)
):
    return await service.login(
        db,
        payload,
        UserRole.CUSTOMER
    )      