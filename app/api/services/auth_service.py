from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from uuid import UUID
from sqlalchemy.orm import Session

from app.api.core.config import settings
from app.api.core.security import verify_password, create_access_token, decode_token, create_refresh_token

from app.api.repositories.user_repository import UserRepository
from app.api.repositories.refresh_token_repository import RefreshRepository


class AuthService:
    def __init__(self,db : Session):
        self.user_repository = UserRepository(db)
        self.refresh_token_repository = RefreshRepository()
        
        
    def login(self,form_data: OAuth2PasswordRequestForm,) :
        user = self.user_repository.get_user_by_email(form_data.username)
        
        if user is None:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid email or password"
            )
       
        if not verify_password(
           form_data.password,
           user.password_hash,
        ):
           raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid email or password"
            )
           
        payload = {
                "sub": str(user.user_id),
                "email": user.email,
                "username":user.user_name,
            }
           
        access_token = create_access_token(payload)
        
        refresh_token = create_refresh_token(payload)
        
        self.refresh_token_repository.save_refresh_token(
            user_id = user.user_id,
            refresh_token = refresh_token,
            expire_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )
        
        return {
            "access_token":access_token,
            "refresh_token":refresh_token,
            "token_type":"bearer"
        }
        
        
    def refresh_access_token(
        self,
        refresh_token: str,
    ):
        try:
            payload = decode_token(refresh_token)

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
        )

        user_id = UUID(payload["sub"])

        stored_token = self.refresh_token_repository.get_refresh_token(user_id)

        if stored_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired",
            )

        if stored_token != refresh_token:
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

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
        
        
    def logout(
        self,
        refresh_token: str,
    ) -> None:
        try:
            payload = decode_token(refresh_token)

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        user_id = UUID(payload["sub"])

        stored_token = self.refresh_token_repository.get_refresh_token(user_id)

        if stored_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session already expired",
            )

        if stored_token != refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        self.refresh_token_repository.delete_refresh_token(user_id)