from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.api.models.users_model import User
from app.api.repositories.user_repository import UserRepository
from app.api.schemas.user_schema import UserCreate, UserUpdate

class UserService:
    def __init__(self,db: Session):
        self.user_repository = UserRepository(db)
        
    def create_user(self,userdata: UserCreate) -> User:
        
        existing_email = self.user_repository.get_user_by_email(userdata.email)
        existing_username = self.user_repository.get_user_by_username(userdata.user_name)
       
        if existing_email is not None:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = 'Email already exists'
            )
            
        if existing_username:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = 'Username already exists'
            )
            
        user = User(
            user_name = userdata.user_name,
            email = userdata.email,
            password_hash = userdata.password_hash
        )

        return self.user_repository.create_user(user)
        
        
    def get_user_by_id(self, user_id: UUID) -> User:
        user = self.user_repository.get_user_by_id(user_id)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user
    
    def get_all_users(self) -> list[User]:
        return self.user_repository.get_all_users()
        
    
    def update_user(
            self,
            user_id: UUID,
            userdata: UserUpdate
        ) -> User:
        
        user = self.user_repository.get_user_by_id(user_id)
       
        if user is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = 'User not found'
            )
        update_data = userdata.model_dump(exclude_unset = True)
        
        for key,value in update_data.items():
            setattr(user, key, value)
        
        return self.user_repository.update_user(user) 
    
    
    def delete_user(
            self,
            user_id: UUID,
        ) -> None:
        
        user = self.user_repository.get_user_by_id(user_id)
       
        if user is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = 'User not found'
            )

        
        self.user_repository.delete_user(user) 
        
        