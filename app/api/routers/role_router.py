from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.core.dependencies import get_current_user
from app.api.core.rbac import require_roles
from app.api.database.db_config import get_db
from app.api.enums.roles import RoleName
from app.api.models.users_model import User
from app.api.schemas.query_schema import RoleQueryParams
from app.api.schemas.role_schema import RoleCreate, RoleResponse, RoleUpdate
from app.api.services.error_service import (
    CREATE_RESPONSES,
    PROTECTED_RESPONSES,
    RESOURCE_RESPONSES,
)
from app.api.services.role_service import RoleService

router = APIRouter(prefix="/roles", tags=["Roles"])


def get_role_service(db: Session = Depends(get_db)):
    return RoleService(db)


# @router.post(
#     "",
#     response_model=RoleResponse,
#     status_code=status.HTTP_201_CREATED,
#     responses=CREATE_RESPONSES
# )
# def create_role(
#     roledata: RoleCreate,
#     service: RoleService = Depends(get_role_service),
#     current_user: User = Depends(
#         require_roles([RoleName.ADMIN])
#     )
# ):

#     return service.create_role(roledata)


@router.get("", response_model=list[RoleResponse], responses=PROTECTED_RESPONSES)
def get_roles(
    query: RoleQueryParams = Depends(),
    service: RoleService = Depends(get_role_service),
    current_user: User = Depends(get_current_user),
):

    return service.get_all_roles(query, current_user)


@router.get("/{id}", response_model=RoleResponse, responses=RESOURCE_RESPONSES)
def get_role(
    id: UUID,
    service: RoleService = Depends(get_role_service),
    current_user: User = Depends(get_current_user),
):

    return service.get_role_by_id(
        role_id=id,
        current_user=current_user,
    )


# @router.patch(
#     "/{id}",
#     response_model=RoleResponse,
#     responses=RESOURCE_RESPONSES
# )
# def update_role(
#     id: UUID,
#     roledata: RoleUpdate,
#     service: RoleService = Depends(get_role_service),
#     current_user: User = Depends(
#         require_roles([RoleName.ADMIN])
#     )
# ):

#     return service.update_role(
#         role_id = id,
#         roledata = roledata
#     )


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, responses=RESOURCE_RESPONSES
)
def delete_role(
    id: UUID,
    service: RoleService = Depends(get_role_service),
    current_user: User = Depends(require_roles([RoleName.ADMIN])),
):

    service.delete_role(role_id=id)

    return None
