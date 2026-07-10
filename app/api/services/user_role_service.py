from fastapi import HTTPException, status
from uuid import UUID

from sqlalchemy.orm import Session

from app.api.models.user_role import UserRole
from app.api.schemas.query_schema import UserRoleQueryParams

from app.api.repositories.user_repository import UserRepository
from app.api.repositories.role_repository import RoleRepository
from app.api.repositories.user_role_repository import UserRoleRepository
from app.api.schemas.user_role_schema import UserRoleCreate, UserRoleUpdate


class UserRoleService:
    def __init__(self, db: Session):
        self.user_role_repository = UserRoleRepository(db)
        self.role_repository = RoleRepository(db)
        self.user_repository = UserRepository(db)
        
        
    def create_user_role(
        self,
        user_role_data: UserRoleCreate,
    ) -> UserRole:

        user = self.user_repository.get_user_by_id(
            user_role_data.user_id
        )
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        role = self.role_repository.get_role_by_id(
            user_role_data.role_id
        )
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )


        assigned_by = self.user_repository.get_user_by_id(
            user_role_data.assigned_by
        )
        if assigned_by is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned by user not found",
            )

        existing = self.user_role_repository.get_user_role(
            user_role_data.user_id,
            user_role_data.role_id,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already has this role",
            )

        user_role = UserRole(
            user_id = user_role_data.user_id,
            role_id = user_role_data.role_id,
            assigned_by = user_role_data.assigned_by,
        )

        return self.user_role_repository.create_user_role(
            user_role
        )
        
  
    def get_all_user_roles(
        self,
        query: UserRoleQueryParams,
    ):
        return self.user_role_repository.get_all_user_roles(query)
    
    
    def get_user_role_by_id(
        self,
        user_role_id: UUID
    ) -> UserRole:
            user_role = self.user_role_repository.get_user_role_by_id(user_role_id)
        
            if user_role is None:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND,
                    detail = "User role not found",
                )
            return user_role
  
    def update_user_role(
        self,
        user_role_id: UUID,
        user_role_data: UserRoleUpdate
    ) -> UserRole:
        user_role = self.user_role_repository.get_user_role_by_id(user_role_id)
        
        if user_role is None:
            raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND,
                    detail = "User role not found"
            )
            
        update_data = user_role_data.model_dump(exclude_unset = True)
        
        if "role_id" in update_data:
            role = self.role_repository.get_role_by_id(
                update_data["role_id"]
            )

            if role is None:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND,
                    detail = "Role not found",
                )

            duplicate = self.user_role_repository.get_user_role(
                user_role.user_id,
                update_data["role_id"],
            )

            if (
                duplicate
                and duplicate.id != user_role.id
            ):
                raise HTTPException(
                    status_code = status.HTTP_409_CONFLICT,
                    detail = "User already has this role",
                )
            
        for key, value in update_data.items():
                setattr(user_role,key, value)
                
        return self.user_role_repository.update_user_role(user_role)
        
    def delete_user_role(
        self,
        user_role_id: UUID
    ) -> None:
        user_role = self.user_role_repository.get_user_role_by_id(user_role_id)
            
        if user_role is None:
            raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND,
                    detail = "User role not found"
            )
                
        self.user_role_repository.delete_user_role(user_role)
