from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.core.logging import get_logger
from app.api.models.user_role import UserRole
from app.api.repositories.role_repository import RoleRepository
from app.api.repositories.user_repository import UserRepository
from app.api.repositories.user_role_repository import UserRoleRepository
from app.api.schemas.query_schema import UserRoleQueryParams
from app.api.schemas.user_role_schema import (
    UserRoleCreate,
    UserRoleUpdate,
)

logger = get_logger(__name__)


class UserRoleService:
    def __init__(self, db: Session):
        self.user_role_repository = UserRoleRepository(db)
        self.role_repository = RoleRepository(db)
        self.user_repository = UserRepository(db)

    def create_user_role(
        self,
        user_role_data: UserRoleCreate,
    ) -> UserRole:

        logger.info(
            "Assigning role %s to user %s",
            user_role_data.role_id,
            user_role_data.user_id,
        )

        user = self.user_repository.get_user_by_id(
            user_role_data.user_id,
        )

        if user is None:
            logger.warning(
                "User %s not found",
                user_role_data.user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        role = self.role_repository.get_role_by_id(
            user_role_data.role_id,
        )

        if role is None:
            logger.warning(
                "Role %s not found",
                user_role_data.role_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )

        assigned_by = self.user_repository.get_user_by_id(
            user_role_data.assigned_by,
        )

        if assigned_by is None:
            logger.warning(
                "Assigned-by user %s not found",
                user_role_data.assigned_by,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned by user not found",
            )

        existing = self.user_role_repository.get_user_role(
            user_role_data.user_id,
            user_role_data.role_id,
        )

        if existing:
            logger.warning(
                "User %s already has role %s",
                user_role_data.user_id,
                user_role_data.role_id,
            )

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already has this role",
            )

        user_role = UserRole(
            user_id=user_role_data.user_id,
            role_id=user_role_data.role_id,
            assigned_by=user_role_data.assigned_by,
        )

        user_role = self.user_role_repository.create_user_role(
            user_role,
        )

        logger.info(
            "Assigned role '%s' (%s) to user '%s' (%s)",
            role.role_name,
            role.role_id,
            user.user_name,
            user.user_id,
        )

        return user_role
        
  
    def get_all_user_roles(
        self,
        query: UserRoleQueryParams,
    ) -> list[UserRole]:

        logger.info(
            "Fetching user-role mappings (page=%s, limit=%s, search=%s)",
            query.page,
            query.limit,
        )

        user_roles = self.user_role_repository.get_all_user_roles(
            query,
        )

        logger.info(
            "Retrieved %d user-role mappings from database",
            len(user_roles),
        )

        return user_roles

    def get_user_role_by_id(
        self,
        user_role_id: UUID,
    ) -> UserRole:

        logger.info(
            "Fetching user-role mapping %s",
            user_role_id,
        )

        user_role = self.user_role_repository.get_user_role_by_id(
            user_role_id,
        )

        if user_role is None:
            logger.warning(
                "User-role mapping %s not found",
                user_role_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User role not found",
            )

        logger.info(
            "Retrieved user-role mapping %s",
            user_role_id,
        )

        return user_role
  
    def update_user_role(
            self,
            user_role_id: UUID,
            user_role_data: UserRoleUpdate,
        ) -> UserRole:

            logger.info(
                "Updating user-role mapping %s",
                user_role_id,
            )

            user_role = self.user_role_repository.get_user_role_by_id(
                user_role_id,
            )

            if user_role is None:
                logger.warning(
                    "User-role mapping %s not found",
                    user_role_id,
                )

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User role not found",
                )

            update_data = user_role_data.model_dump(
                exclude_unset=True,
            )

            if "role_id" in update_data:
                role = self.role_repository.get_role_by_id(
                    update_data["role_id"],
                )

                if role is None:
                    logger.warning(
                        "Role %s not found",
                        update_data["role_id"],
                    )

                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Role not found",
                    )

                duplicate = self.user_role_repository.get_user_role(
                    user_role.user_id,
                    update_data["role_id"],
                )

                if (
                    duplicate
                    and duplicate.id != user_role.id
                ):
                    logger.warning(
                        "User %s already has role %s",
                        user_role.user_id,
                        update_data["role_id"],
                    )

                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="User already has this role",
                    )

            for key, value in update_data.items():
                setattr(
                    user_role,
                    key,
                    value,
                )

            user_role = self.user_role_repository.update_user_role(
                user_role,
            )

            logger.info(
                "Updated user-role mapping %s",
                user_role.id,
            )

            if update_data:
                logger.info(
                    "Updated fields: %s",
                    ", ".join(update_data.keys()),
                )

            return user_role

    def delete_user_role(
        self,
        user_role_id: UUID,
    ) -> None:

        logger.info(
            "Deleting user-role mapping %s",
            user_role_id,
        )

        user_role = self.user_role_repository.get_user_role_by_id(
            user_role_id,
        )

        if user_role is None:
            logger.warning(
                "User-role mapping %s not found",
                user_role_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User role not found",
            )

        self.user_role_repository.delete_user_role(
            user_role,
        )

        logger.info(
            "Deleted user-role mapping %s",
            user_role_id,
        )
        
        
