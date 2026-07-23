from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.core.authorization import is_admin
from app.api.core.logging import get_logger
from app.api.models.roles_model import Role
from app.api.models.user_role import UserRole
from app.api.models.users_model import User
from app.api.repositories.cache_repository import CacheRepository
from app.api.repositories.role_repository import RoleRepository
from app.api.repositories.user_repository import UserRepository
from app.api.repositories.user_role_repository import UserRoleRepository
from app.api.schemas.user_role_schema import UserRoleCreate

logger = get_logger(__name__)


class UserRoleService:

    def __init__(
        self,
        db: Session,
    ):
        self.user_role_repository = UserRoleRepository(db)
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)
        self.cache_repository = CacheRepository()

    def assign_role(
        self,
        user_id: UUID,
        role_data: UserRoleCreate,
        current_user: User,
    ) -> UserRole:

        logger.info(
            "Assigning role %s to user %s",
            role_data.role_id,
            user_id,
        )

        if not is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can assign roles",
            )

        user = self.user_repository.get_user_by_id(
            user_id,
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        role = self.role_repository.get_role_by_id(
            role_data.role_id,
        )

        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )

        existing = self.user_role_repository.get_user_role(
            user_id=user_id,
            role_id=role.role_id,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already has this role",
            )

        user_role = UserRole(
            user_id=user_id,
            role_id=role.role_id,
            assigned_by=current_user.user_id,
        )

        created_user_role = self.user_role_repository.create_user_role(user_role)

        self.invalidate_user_role_cache(
            user_id,
        )

        logger.info(
            "Role %s assigned successfully to user %s",
            role.role_id,
            user_id,
        )

        return created_user_role

    def get_user_roles(
        self,
        user_id: UUID,
        current_user: User,
    ) -> list[Role]:

        logger.info(
            "Fetching roles for user %s",
            user_id,
        )

        user = self.user_repository.get_user_by_id(
            user_id,
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if current_user.user_id != user_id and not is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )

        return self.user_role_repository.get_roles_by_user_id(user_id)

    def get_user_role_by_id(
        self,
        user_id: UUID,
        role_id: UUID,
        current_user: User,
    ) -> UserRole:

        if current_user.user_id != user_id and not is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )

        user_role = self.user_role_repository.get_user_role(
            user_id=user_id,
            role_id=role_id,
        )

        if user_role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role assignment not found",
            )

        return user_role

    def remove_role(
        self,
        user_id: UUID,
        role_id: UUID,
        current_user: User,
    ) -> None:

        logger.info(
            "Removing role %s from user %s",
            role_id,
            user_id,
        )

        if not is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can remove roles",
            )

        user_role = self.user_role_repository.get_user_role(
            user_id=user_id,
            role_id=role_id,
        )

        if user_role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role assignment not found",
            )

        self.user_role_repository.delete_user_role(
            user_role,
        )

        self.invalidate_user_role_cache(
            user_id,
        )

        logger.info(
            "Role removed successfully from user %s",
            user_id,
        )

    def invalidate_user_role_cache(
        self,
        user_id: UUID,
    ) -> None:

        self.cache_repository.delete(
            f"taskflow:cache:user_roles:{user_id}",
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:users*",
        )
