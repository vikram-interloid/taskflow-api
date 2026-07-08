from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.api.schemas.token_schema import LoginRequest
from app.api.core.security import verify_password, create_access_token

from app.api.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self,db : Session):
        self.user_repository = UserRepository(db)
        
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
           
        access_token = create_access_token(
            {
                "sub": str(user.user_id),
                "email": user.email,
                "username":user.user_name,
            }
        )
        
        return {
            "access_token":access_token,
            "token_type":"bearer"
        }