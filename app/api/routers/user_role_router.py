from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.core.dependencies import get_current_user
from app.api.core.rbac import require_roles
from app.api.database.db_config import get_db
from app.api.enums.roles import RoleName
from app.api.models.users_model import User
from app.api.schemas.role_schema import RoleResponse
from app.api.schemas.user_role_schema import (
    UserRoleCreate,
    UserRoleResponse,
)
from app.api.services.error_service import (
    CREATE_RESPONSES,
    PROTECTED_RESPONSES,
    RESOURCE_RESPONSES,
)
from app.api.services.user_role_service import UserRoleService


router = APIRouter(
    prefix="/users/{id}/roles",
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
    responses=CREATE_RESPONSES,
)
def assign_role(
    id: UUID,
    request: UserRoleCreate,
    current_user: User = Depends(
        require_roles([RoleName.ADMIN]),
    ),
    service: UserRoleService = Depends(
        get_user_role_service,
    ),
):
    return service.assign_role(
        user_id=id,
        role_data=request,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=list[RoleResponse],
    responses=PROTECTED_RESPONSES,
)
def get_user_roles(
    id: UUID,
    current_user: User = Depends(
        get_current_user,
    ),
    service: UserRoleService = Depends(
        get_user_role_service,
    ),
):
    return service.get_user_roles(
        user_id=id,
        current_user=current_user,
    )


@router.get(
    "/{role_id}",
    response_model=UserRoleResponse,
    responses=RESOURCE_RESPONSES,
)
def get_user_role(
    id: UUID,
    role_id: UUID,
    current_user: User = Depends(
        get_current_user,
    ),
    service: UserRoleService = Depends(
        get_user_role_service,
    ),
):
    return service.get_user_role_by_id(
        user_id=id,
        role_id=role_id,
        current_user=current_user,
    )


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESOURCE_RESPONSES,
)
def remove_role(
    id: UUID,
    role_id: UUID,
    current_user: User = Depends(
        require_roles([RoleName.ADMIN]),
    ),
    service: UserRoleService = Depends(
        get_user_role_service,
    ),
):
    service.remove_role(
        user_id=id,
        role_id=role_id,
        current_user=current_user,
    )

    return None

