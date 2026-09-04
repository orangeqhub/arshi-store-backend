import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError
)

from app.models.models import User, UserRole
from app.repositories.user_repository import UserRepository
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

logger = logging.getLogger(__name__)


class AuthService:

    def __init__(self):
        self.user_repo = UserRepository()

    async def register_admin(self, db, payload):

        try:

            existing = await self.user_repo.get_by_email(
                db,
                payload.email
            )

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists"
                )

            user = User(
                full_name=payload.full_name,
                email=payload.email,
                phone=payload.phone,
                password_hash=hash_password(
                    payload.password
                ),
                role=UserRole.ADMIN
            )

            return await self.user_repo.create(
                db,
                user
            )

        except HTTPException:
            raise

        except IntegrityError as e:

            logger.error(
                f"IntegrityError while registering admin: {str(e)}"
            )

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )

        except SQLAlchemyError as e:

            logger.exception(
                f"Database error while registering admin: {str(e)}"
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )

        except Exception as e:

            logger.exception(
                f"Unexpected error while registering admin: {str(e)}"
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    async def register_user(self, db, payload):

        try:

            existing = await self.user_repo.get_by_email(
                db,
                payload.email
            )

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists"
                )

            user = User(
                full_name=payload.full_name,
                email=payload.email,
                phone=payload.phone,
                password_hash=hash_password(
                    payload.password
                ),
                role=UserRole.CUSTOMER
            )

            return await self.user_repo.create(
                db,
                user
            )

        except HTTPException:
            raise

        except IntegrityError as e:

            logger.error(
                f"IntegrityError while registering user: {str(e)}"
            )

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )

        except SQLAlchemyError as e:

            logger.exception(
                f"Database error while registering user: {str(e)}"
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )

        except Exception as e:

            logger.exception(
                f"Unexpected error while registering user: {str(e)}"
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    async def login(
            self,
            db,
            payload,
            required_role: UserRole
        ):
            try:

                user = await self.user_repo.get_by_email(
                    db,
                    payload.email
                )

                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found"
                    )

                if user.role != required_role:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"{required_role.value.title()} access only"
                    )

                if not verify_password(
                    payload.password,
                    user.password_hash
                ):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials"
                    )

                token = create_access_token(
                    {
                        "sub": str(user.id),
                        "role": user.role.value,
                        "email": user.email
                    }
                )

                return {
                    "success": True,
                    "status_code": 200,
                    "message": "Login successful",
                    "data": {
                        "access_token": token,
                        "token_type": "bearer",
                        "user": {
                            "id": str(user.id),
                            "full_name": user.full_name,
                            "email": user.email,
                            "phone": user.phone,
                            "role": user.role.value,
                            "created_at": user.created_at
                        }
                    }
                }

            except HTTPException:
                raise

            except SQLAlchemyError as e:

                logger.exception(
                    f"Database error during login: {str(e)}"
                )

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database error occurred"
                )

            except Exception as e:

                logger.exception(
                    f"Unexpected error during login: {str(e)}"
                )

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )