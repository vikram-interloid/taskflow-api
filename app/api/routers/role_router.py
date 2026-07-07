from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.database.db_config import get_db
from app.api.schemas.role_schema import RoleCreate,RoleResponse,RoleUpdate
from app.api.services.role_service import RoleService

router = APIRouter(
    prefix = '/roles',
    tags = ["Roles"]
)

def get_role_service(db: Session = Depends(get_db),) -> RoleService:
    return RoleService(db)


@router.post(
    '',
    response_model = RoleResponse,
    status_code = status.HTTP_201_CREATED,
)
def create_role(
    role_data: RoleCreate,
    service: RoleService = Depends(get_role_service)
):
    return service.create_role(role_data)

@router.get(
    '',
    response_model = list[RoleResponse],
    status_code = status.HTTP_200_OK,
)
def get_all_roles(
    service: RoleService = Depends(get_role_service)
):
    return service.get_all_roles()


@router.get(
    '/{role_id}',
    response_model = RoleResponse,
    status_code = status.HTTP_200_OK,
)
def get_role_by_id(
    role_id: UUID,
    service: RoleService = Depends(get_role_service)
):
    return service.get_role_by_id(role_id)


@router.patch(
    '/{role_id}',
    response_model = RoleResponse,
    status_code = status.HTTP_200_OK,
)
def update_role(
    role_id: UUID,
    role_data: RoleUpdate,
    service: RoleService = Depends(get_role_service)
):
    return service.update_role(role_id,role_data)


@router.delete(
    '/{role_id}',
    status_code = status.HTTP_200_OK,
)
def delete_role(
    role_id: UUID,
    service: RoleService = Depends(get_role_service)
):
    return service.delete_role(role_id)