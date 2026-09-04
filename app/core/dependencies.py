from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer

from app.core.security import decode_token

security = HTTPBearer()


async def get_current_user(
    credentials=Depends(security)
):
    try:

        token = credentials.credentials

        payload = decode_token(token)

        return payload

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )


async def get_current_admin(
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin Access Required"
        )

    return current_user


# Backward compatibility
admin_required = get_current_admin