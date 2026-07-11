from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.enums.roles import RoleName

from app.api.core.rbac import require_roles
from app.api.database.db_config import get_db
from app.api.models.users_model import User
from app.api.schemas.query_schema import UserRoleQueryParams
from app.api.schemas.user_role_schema import (
    UserRoleCreate,
    UserRoleResponse,
    UserRoleUpdate,
)
from app.api.services.user_role_service import UserRoleService

router = APIRouter(
    prefix="/user-roles",
    tags=["User Roles"],
)


def get_user_role_service(
    db: Session = Depends(get_db),
) -> UserRoleService:
    return UserRoleService(db)


@router.post(
    "",
    response_model=UserRoleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_role(
    user_role_data: UserRoleCreate,
    service: UserRoleService = Depends(get_user_role_service),
    current_user: User = Depends(
        require_roles([RoleName.ADMIN])
    )
):
    return service.create_user_role(user_role_data)


@router.get(
    "",
    response_model=list[UserRoleResponse],
    status_code=status.HTTP_200_OK,
)
def get_all_user_roles(
    query: UserRoleQueryParams = Depends(),
    service: UserRoleService = Depends(get_user_role_service),
    current_user: User = Depends(
        require_roles([
            RoleName.ADMIN,
            RoleName.MANAGER,
        ])
    )
):
    return service.get_all_user_roles(query)


@router.get(
    "/{user_role_id}",
    response_model=UserRoleResponse,
    status_code=status.HTTP_200_OK,
)
def get_user_role_by_id(
    user_role_id: UUID,
    service: UserRoleService = Depends(get_user_role_service),
    current_user: User = Depends(
        require_roles([
            RoleName.ADMIN,
            RoleName.MANAGER,
        ])
    )
):
    return service.get_user_role_by_id(user_role_id)


@router.patch(
    "/{user_role_id}",
    response_model=UserRoleResponse,
    status_code=status.HTTP_200_OK,
)
def update_user_role(
    user_role_id: UUID,
    user_role_data: UserRoleUpdate,
    service: UserRoleService = Depends(get_user_role_service),
    current_user: User = Depends(
        require_roles([RoleName.ADMIN])
    )
):
    return service.update_user_role(
        user_role_id,
        user_role_data,
    )


@router.delete(
    "/{user_role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user_role(
    user_role_id: UUID,
    service: UserRoleService = Depends(get_user_role_service),
    current_user: User = Depends(
        require_roles([
            RoleName.ADMIN
            ])
    )
):
    service.delete_user_role(user_role_id)
    
    