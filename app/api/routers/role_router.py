from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.models.users_model import User
from app.api.core.dependencies import get_current_user
from app.api.core.rbac import require_roles
from app.api.database.db_config import get_db
from app.api.enums.roles import RoleName
from app.api.schemas.query_schema import RoleQueryParams
from app.api.schemas.role_schema import RoleCreate, RoleResponse, RoleUpdate
from app.api.services.role_service import RoleService

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)



def get_role_service(
    db: Session = Depends(get_db)
):
    return RoleService(db)



@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED
)
def create_role(
    roledata: RoleCreate,
    service: RoleService = Depends(get_role_service),
    current_user: User = Depends(
        require_roles([RoleName.ADMIN])
    )
):

    return service.create_role(roledata)



@router.get(
    "/",
    response_model=list[RoleResponse]
)
def get_roles(
    query: RoleQueryParams = Depends(),
    service: RoleService = Depends(get_role_service),
    current_user: User = Depends(
            require_roles([
                RoleName.ADMIN,
                RoleName.MANAGER,
            ])
        )    
):

    return service.get_all_roles(query)



@router.get(
    "/{role_id}",
    response_model=RoleResponse
)
def get_role(
    role_id: UUID,
    service: RoleService = Depends(get_role_service),
    current_user: User = Depends(
            require_roles([
                RoleName.ADMIN,
                RoleName.MANAGER,
            ])
        )    
):

    return service.get_role_by_id(
        role_id
    )



@router.patch(
    "/{role_id}",
    response_model=RoleResponse
)
def update_role(
    role_id: UUID,
    roledata: RoleUpdate,
    service: RoleService = Depends(get_role_service),
    current_user: User = Depends(
        require_roles([RoleName.ADMIN])
    )    
):

    return service.update_role(
        role_id,
        roledata
    )



@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_role(
    role_id: UUID,
    service: RoleService = Depends(get_role_service),
    current_user: User = Depends(
        require_roles([RoleName.ADMIN])
    )    
):

    service.delete_role(
        role_id
    )

    return None

