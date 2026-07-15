from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.core.authorization import can_access_user, is_admin
from app.api.core.logging import get_logger
from app.api.core.security import hash_password
from app.api.enums.roles import RoleName
from app.api.models.users_model import User
from app.api.repositories.cache_repository import CacheRepository
from app.api.repositories.user_repository import UserRepository
from app.api.repositories.user_role_repository import UserRoleRepository
from app.api.schemas.query_schema import UserQueryParams
from app.api.schemas.user_schema import UserCreate, UserUpdate

logger = get_logger(__name__)

class UserService:
    def __init__(self,db: Session):
        self.user_repository = UserRepository(db)
        self.user_role_repository = UserRoleRepository(db)
        self.cache_repository = CacheRepository()
        
    def create_user(
        self,
        userdata: UserCreate,
    ) -> User:

        logger.info(
            "Creating user '%s'",
            userdata.email,
        )

        existing_email = self.user_repository.get_user_by_email(
            userdata.email,
        )

        existing_username = self.user_repository.get_user_by_username(
            userdata.user_name,
        )

        if existing_email is not None:
            logger.warning(
                "Email '%s' already exists",
                userdata.email,
            )

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

        if existing_username is not None:
            logger.warning(
                "Username '%s' already exists",
                userdata.user_name,
            )

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists",
            )

        user = User(
            user_name=userdata.user_name,
            email=userdata.email,
            password_hash=hash_password(
                userdata.password_hash,
            ),
        )

        user = self.user_repository.create_user(
            user,
        )

        logger.info(
            "User '%s' created successfully",
            user.email,
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:users*",
        )

        logger.info(
            "Invalidated cache pattern 'taskflow:cache:users*'",
        )

        return user
        
        
    def get_user_by_id(
        self,
        user_id: UUID,
        current_user: User
    ) -> User:

        cache_key = f"taskflow:cache:user:{user_id}"

        logger.info(
            "Checking cache '%s'",
            cache_key,
        )
        can_access_user(
            current_user=current_user,
            target_user_id=user_id,
        )

        cached_user = self.cache_repository.get(
            cache_key,
        )

        if cached_user is not None:
            logger.info(
                "Cache HIT '%s'",
                cache_key,
            )

            return cached_user

        logger.info(
            "Cache MISS '%s'",
            cache_key,
        )

        user = self.user_repository.get_user_by_id(
            user_id,
        )

        if user is None:
            logger.warning(
                "User %s not found",
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        logger.info(
            "Retrieved user '%s' (%s) from database",
            user.email,
            user.user_id,
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

        logger.info(
            "Cached user '%s' for 300 seconds",
            user.email,
        )

        return user_data
    
    
    def get_all_users(
        self,
        query: UserQueryParams,
        current_user: User,
    ) -> dict:

        cache_key = (
            f"taskflow:cache:users:"
            f"admin={is_admin(current_user)}:"
            f"user={current_user.user_id}:"
            f"page={query.page}:"
            f"limit={query.limit}:"
            f"email={query.email}:"
            f"search={query.search}:"
            f"sort_by={query.sort_by}:"
            f"order={query.order}"
        )

        logger.info(
            "Checking cache '%s'",
            cache_key,
        )

        cached_response = self.cache_repository.get(
            cache_key,
        )

        if cached_response is not None:
            logger.info(
                "Cache HIT '%s'",
                cache_key,
            )

            return cached_response

        logger.info(
            "Cache MISS '%s'",
            cache_key,
        )

        if is_admin(current_user):
            users, total = self.user_repository.get_all_users(query)
        else:
            users = [
                self.user_repository.get_user_by_id(
                    current_user.user_id,
                )
            ]
            total = len(users)

        logger.info(
            "Retrieved %d users from database",
            len(users),
        )

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

        response = {
            "page": query.page,
            "limit": query.limit,
            "total": total,
            "data": user_list,
        }

        self.cache_repository.set(
            key=cache_key,
            value=response,
            expire=300,
        )

        logger.info(
            "Cached %d users for 300 seconds",
            len(user_list),
        )

        return response
        
    
    def update_user(
        self,
        user_id: UUID,
        userdata: UserUpdate,
        current_user: User,
    ) -> User:

        logger.info(
            "Updating user %s",
            user_id,
        )

        user = self.user_repository.get_user_by_id(
            user_id,
        )

        if user is None:
            logger.warning(
                "User %s not found",
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        roles = self.user_role_repository.get_roles_by_user_id(
            current_user.user_id,
        )

        is_admin = any(
            role.role_name == RoleName.ADMIN
            for role in roles
        )

        if current_user.user_id != user.user_id and not is_admin:
            logger.warning(
                "User %s is not authorized to update user %s",
                current_user.user_id,
                user.user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to update this user",
            )

        update_data = userdata.model_dump(
            exclude_unset=True,
        )

        for key, value in update_data.items():
            setattr(
                user,
                key,
                value,
            )

        user = self.user_repository.update_user(
            user,
        )

        logger.info(
            "Updated user '%s' (%s)",
            user.email,
            user.user_id,
        )

        if update_data:
            logger.info(
                "Updated fields: %s",
                ", ".join(update_data.keys()),
            )

        self.cache_repository.delete(
            f"taskflow:cache:user:{user.user_id}",
        )

        logger.info(
            "Invalidated cache 'taskflow:cache:user:%s'",
            user.user_id,
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:users*",
        )

        logger.info(
            "Invalidated cache pattern 'taskflow:cache:users*'",
        )

        return user
    
    
    def delete_user(
        self,
        user_id: UUID,
        current_user: User,
    ) -> None:

        logger.info(
            "Deleting user %s",
            user_id,
        )

        user = self.user_repository.get_user_by_id(
            user_id,
        )

        if user is None:
            logger.warning(
                "User %s not found",
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        roles = self.user_role_repository.get_roles_by_user_id(
            current_user.user_id,
        )

        is_admin = any(
            role.role_name == RoleName.ADMIN
            for role in roles
        )

        if current_user.user_id != user.user_id and not is_admin:
            logger.warning(
                "User %s is not authorized to delete user %s",
                current_user.user_id,
                user.user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to delete this user",
            )

        self.user_repository.delete_user(
            user,
        )

        logger.info(
            "Deleted user '%s' (%s)",
            user.email,
            user.user_id,
        )

        self.cache_repository.delete(
            f"taskflow:cache:user:{user.user_id}",
        )

        logger.info(
            "Invalidated cache 'taskflow:cache:user:%s'",
            user.user_id,
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:users*",
        )

        logger.info(
            "Invalidated cache pattern 'taskflow:cache:users*'",
        )
            
        