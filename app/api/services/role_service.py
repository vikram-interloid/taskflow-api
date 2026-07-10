from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.query_schema import RoleQueryParams

from app.api.models.roles_model import Role
from app.api.repositories.cache_repository import CacheRepository
from app.api.repositories.role_repository import RoleRepository
from app.api.schemas.role_schema import RoleCreate, RoleUpdate


class RoleService:

    def __init__(self, db: Session):
        self.role_repository = RoleRepository(db)
        self.cache_repository = CacheRepository()


    def create_role(
        self,
        roledata: RoleCreate
    ) -> Role:

        existing_role = self.role_repository.get_role_by_name(
            roledata.role_name
        )

        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role name already exists",
            )


        role = Role(
            role_name=roledata.role_name
        )


        role = self.role_repository.create_role(role)


        self.cache_repository.delete_pattern(
            "taskflow:cache:roles*"
        )


        return role



    def get_role_by_id(
        self,
        role_id: UUID
    ) -> Role:


        role = self.role_repository.get_role_by_id(
            role_id
        )


        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )


        return role



    def get_all_roles(
        self,
        query: RoleQueryParams
    ) -> list[dict[str, Any]]:

        cache_key = (
            f"taskflow:cache:roles:"
            f"{query.search}:"
            f"{query.sort_by}:"
            f"{query.order}:"
            f"{query.page}:"
            f"{query.limit}"
        )


        # Check Redis cache
        cached_roles = self.cache_repository.get(
            cache_key
        )


        if cached_roles is not None:
            return cached_roles



        # Fetch from database
        roles = self.role_repository.get_all_roles(
            query
        )


        # Convert SQLAlchemy objects into JSON serializable data
        role_list = [
            {
                "role_id": str(role.role_id),
                "role_name": role.role_name,
                "created_at": role.created_at.isoformat(),
            }
            for role in roles
        ]


        # Store in Redis
        self.cache_repository.set(
            key=cache_key,
            value=role_list,
            expire=3600,
        )


        return role_list



    def update_role(
        self,
        role_id: UUID,
        roledata: RoleUpdate
    ) -> Role:


        role = self.role_repository.get_role_by_id(
            role_id
        )


        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )


        update_data = roledata.model_dump(
            exclude_unset=True
        )


        if "role_name" in update_data:

            existing_role = self.role_repository.get_role_by_name(
                update_data["role_name"]
            )


            if (
                existing_role
                and existing_role.role_id != role.role_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Role name already exists",
                )


        for key, value in update_data.items():
            setattr(
                role,
                key,
                value
            )


        role = self.role_repository.update_role(
            role
        )


        self.cache_repository.delete_pattern(
            "taskflow:cache:roles*"
        )


        return role



    def delete_role(
        self,
        role_id: UUID
    ) -> None:


        role = self.role_repository.get_role_by_id(
            role_id
        )


        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )


        self.role_repository.delete_role(
            role
        )


        self.cache_repository.delete_pattern(
            "taskflow:cache:roles*"
        )