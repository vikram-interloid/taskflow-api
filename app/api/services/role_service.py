from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.api.models.roles_model import Role
from app.api.repositories.role_repository import RoleRepository
from app.api.schemas.role_schema import RoleCreate, RoleUpdate


class RoleService:
    def __init__(self,db: Session):
        self.role_repository = RoleRepository(db)
        
    def create_role(self,roledata: RoleCreate) -> Role:
        
        existing_role = self.role_repository.get_role_by_name(roledata.role_name)
            
        if existing_role:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = 'Role name already exists'
            )
            
        role = Role(
            role_name = roledata.role_name,
        )

        return self.role_repository.create_role(role)
        
        
    def get_role_by_id(self, role_id: UUID) -> Role:
        role = self.role_repository.get_role_by_id(role_id)
        
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )

        return role
    
    def get_all_roles(self) -> list[Role]:
        return self.role_repository.get_all_roles()
        
    
    def update_role(
            self,
            role_id: UUID,
            roledata: RoleUpdate
        ) -> Role:
        
        role = self.role_repository.get_role_by_id(role_id)
       
        if role is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = 'Role not found'
            )
        update_data = roledata.model_dump(exclude_unset = True)
        
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
            setattr(role, key, value)
        
        return self.role_repository.update_role(role) 
    
    
    def delete_role(
            self,
            role_id: UUID,
        ) -> None:
        
        role = self.role_repository.get_role_by_id(role_id)
       
        if role is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = 'Role not found'
            )
        
        self.role_repository.delete_role(role) 
        
        