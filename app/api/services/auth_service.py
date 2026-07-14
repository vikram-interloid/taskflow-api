from uuid import UUID

from fastapi import HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.core.logging import get_logger

from app.api.core.config import settings
from app.api.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.api.repositories.refresh_token_repository import RefreshRepository
from app.api.repositories.user_repository import UserRepository
from app.api.schemas.token_schema import LoginRequest

logger = get_logger(__name__)

class AuthService:
    def __init__(self,db : Session):
        self.user_repository = UserRepository(db)
        self.refresh_token_repository = RefreshRepository()
        
        
    def login(
        self,
        login_data: LoginRequest
    ) -> dict:

        logger.info(
            "Login attempt for '%s'",
            login_data.email,
        )

        user = self.user_repository.get_user_by_email(
            login_data.email,
        )

        if user is None:
            logger.warning(
                "Login failed for '%s': user not found",
                login_data.email,
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(
            login_data.password,
            user.password_hash,
        ):
            logger.warning(
                "Login failed for '%s': invalid password",
                login_data.email,
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        payload = {
            "sub": str(user.user_id),
            "email": user.email,
            "username": user.user_name,
        }

        access_token = create_access_token(
            payload,
        )

        refresh_token = create_refresh_token(
            payload,
        )

        self.refresh_token_repository.save_refresh_token(
            user_id=user.user_id,
            refresh_token=refresh_token,
            expire_seconds=settings.REFRESH_TOKEN_EXPIRE_DAYS
            * 24
            * 60
            * 60,
        )

        logger.info(
            "User '%s' logged in successfully",
            user.email,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
        
        
    def refresh_access_token(
        self,
        refresh_token: str,
    ) -> dict:
        logger.info(
            "Refreshing access token",
        )

        try:
            payload = decode_token(
                refresh_token,
            )

        except ValueError as err:
            logger.warning(
                "Refresh token is invalid or expired",
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            ) from err

        user_id = UUID(
            payload["sub"],
        )

        logger.info(
            "Looking up refresh token for user %s",
            user_id,
        )

        stored_token = self.refresh_token_repository.get_refresh_token(
            user_id,
        )

        if stored_token is None:
            logger.warning(
                "No active refresh token found for user %s",
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired",
            )

        if stored_token != refresh_token:
            logger.warning(
                "Refresh token mismatch for user %s",
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        access_token = create_access_token(
            {
                "sub": payload["sub"],
                "email": payload["email"],
                "username": payload["username"],
            }
        )

        logger.info(
            "Access token refreshed successfully for user %s",
            user_id,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
        
        
    def logout(
        self,
        refresh_token: str,
    ) -> None:

        logger.info(
            "Logout requested",
        )

        try:
            payload = decode_token(
                refresh_token,
            )

        except ValueError as err:
            logger.warning(
                "Logout failed: refresh token is invalid or expired",
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            ) from err

        if payload.get("type") != "refresh":
            logger.warning(
                "Logout failed: invalid token type",
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        user_id = UUID(
            payload["sub"],
        )

        logger.info(
            "Looking up refresh token for user %s",
            user_id,
        )

        stored_token = self.refresh_token_repository.get_refresh_token(
            user_id,
        )

        if stored_token is None:
            logger.warning(
                "Logout failed: no active session found for user %s",
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session already expired",
            )

        if stored_token != refresh_token:
            logger.warning(
                "Logout failed: refresh token mismatch for user %s",
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        self.refresh_token_repository.delete_refresh_token(
            user_id,
        )

        logger.info(
            "User %s logged out successfully",
            user_id,
        )
        
        