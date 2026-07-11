from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.core.logging import get_logger
from app.api.models.roles_model import Role
from app.api.repositories.cache_repository import CacheRepository
from app.api.repositories.role_repository import RoleRepository
from app.api.schemas.query_schema import RoleQueryParams
from app.api.schemas.role_schema import RoleCreate, RoleUpdate

logger = get_logger(__name__)

class RoleService:
    def __init__(self, db: Session):
        self.role_repository = RoleRepository(db)
        self.cache_repository = CacheRepository()

    def create_role(
        self,
        roledata: RoleCreate,
    ) -> Role:

        logger.info(
            "Creating role '%s'",
            roledata.role_name,
        )

        existing_role = self.role_repository.get_role_by_name(
            roledata.role_name,
        )

        if existing_role:
            logger.warning(
                "Role '%s' already exists",
                roledata.role_name,
            )

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role name already exists",
            )

        role = Role(
            role_name=roledata.role_name,
        )

        role = self.role_repository.create_role(
            role,
        )

        logger.info(
            "Role '%s' created successfully",
            role.role_name,
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:roles*",
        )

        logger.info(
            "Invalidated cache pattern 'taskflow:cache:roles*'",
        )

        return role

    def get_role_by_id(
        self,
        role_id: UUID,
    ) -> Role:

        logger.info(
            "Fetching role %s",
            role_id,
        )

        role = self.role_repository.get_role_by_id(
            role_id,
        )

        if role is None:
            logger.warning(
                "Role %s not found",
                role_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )

        logger.info(
            "Retrieved role %s",
            role_id,
        )

        return role

    def get_all_roles(
        self,
        query: RoleQueryParams,
    ) -> list[dict[str, Any]]:

        cache_key = (
            f"taskflow:cache:roles:"
            f"{query.search}:"
            f"{query.sort_by}:"
            f"{query.order}:"
            f"{query.page}:"
            f"{query.limit}"
        )

        logger.info(
            "Checking cache '%s'",
            cache_key,
        )

        cached_roles = self.cache_repository.get(
            cache_key,
        )

        if cached_roles is not None:
            logger.info(
                "Cache HIT '%s'",
                cache_key,
            )
            return cached_roles

        logger.info(
            "Cache MISS '%s'",
            cache_key,
        )

        roles = self.role_repository.get_all_roles(
            query,
        )

        logger.info(
            "Retrieved %d roles from database",
            len(roles),
        )

        role_list = [
            {
                "role_id": str(role.role_id),
                "role_name": role.role_name,
                "created_at": role.created_at.isoformat(),
            }
            for role in roles
        ]

        self.cache_repository.set(
            key=cache_key,
            value=role_list,
            expire=3600,
        )

        logger.info(
            "Cached %d roles for 3600 seconds",
            len(role_list),
        )

        return role_list

    def update_role(
        self,
        role_id: UUID,
        roledata: RoleUpdate,
    ) -> Role:

        logger.info(
            "Updating role %s",
            role_id,
        )

        role = self.role_repository.get_role_by_id(
            role_id,
        )

        if role is None:
            logger.warning(
                "Role %s not found",
                role_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )

        update_data = roledata.model_dump(
            exclude_unset=True,
        )

        if "role_name" in update_data:
            existing_role = self.role_repository.get_role_by_name(
                update_data["role_name"],
            )

            if (
                existing_role
                and existing_role.role_id != role.role_id
            ):
                logger.warning(
                    "Role '%s' already exists",
                    update_data["role_name"],
                )

                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Role name already exists",
                )

        for key, value in update_data.items():
            setattr(
                role,
                key,
                value,
            )

        role = self.role_repository.update_role(
            role,
        )

        logger.info(
            "Role %s updated successfully",
            role_id,
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:roles*",
        )

        logger.info(
            "Invalidated cache pattern 'taskflow:cache:roles*'",
        )

        return role

    def delete_role(
        self,
        role_id: UUID,
    ) -> None:

        logger.info(
            "Deleting role %s",
            role_id,
        )

        role = self.role_repository.get_role_by_id(
            role_id,
        )

        if role is None:
            logger.warning(
                "Role %s not found",
                role_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )

        self.role_repository.delete_role(
            role,
        )

        logger.info(
            "Role %s deleted successfully",
            role_id,
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:roles*",
        )

        logger.info(
            "Invalidated cache pattern 'taskflow:cache:roles*'",
        )
        
        