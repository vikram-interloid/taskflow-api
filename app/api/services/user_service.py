from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.api.core.security import hash_password

from app.api.schemas.query_schema import UserQueryParams
from app.api.repositories.cache_repository import CacheRepository

from app.api.models.users_model import User
from app.api.repositories.user_repository import UserRepository
from app.api.schemas.user_schema import UserCreate, UserUpdate

class UserService:
    def __init__(self,db: Session):
        self.user_repository = UserRepository(db)
        self.cache_repository = CacheRepository()
        
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
            password_hash = hash_password(userdata.password_hash)
        )

        user = self.user_repository.create_user(user)

        self.cache_repository.delete_pattern(
            "taskflow:cache:users*"
        )

        return user
        
        
    def get_user_by_id(
        self,
        user_id: UUID,
    ) -> User | dict:

        cache_key = f"taskflow:cache:user:{user_id}"

        cached_user = self.cache_repository.get(cache_key)

        if cached_user is not None:
            return cached_user

        user = self.user_repository.get_user_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user_data = {
            "user_id": str(user.user_id),
            "user_name": user.user_name,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }

        self.cache_repository.set(
            key=cache_key,
            value=user_data,
            expire=300,
        )

        return user_data
    
    
    def get_all_users(
        self,
        query: UserQueryParams,
    ):

        cache_key = (
            f"taskflow:cache:users:"
            f"page={query.page}:"
            f"limit={query.limit}:"
            f"search={query.search}:"
            f"sort={query.sort_by}:"
            f"order={query.order}"
        )

        cached_users = self.cache_repository.get(cache_key)

        if cached_users is not None:
            return cached_users

        users = self.user_repository.get_all_users(query)

        user_list = [
            {
                "user_id": str(user.user_id),
                "user_name": user.user_name,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            }
            for user in users
        ]

        self.cache_repository.set(
            key=cache_key,
            value=user_list,
            expire=300,
        )

        return user_list
        
    
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
        
        user = self.user_repository.update_user(user)

        self.cache_repository.delete(
            f"taskflow:cache:user:{user.user_id}"
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:users*"
        )

        return user
    
    
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

        user_id = user.user_id

        self.user_repository.delete_user(user)

        self.cache_repository.delete(
            f"taskflow:cache:user:{user_id}"
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:users*"
        )
        
        