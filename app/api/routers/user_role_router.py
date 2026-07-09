from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.core.dependencies import get_current_user

from app.api.database.db_config import get_db
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


def get_user_role_service(db: Session = Depends(get_db),) -> UserRoleService:
    return UserRoleService(db)


@router.post(
    "",
    response_model=UserRoleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_role(
    user_role_data: UserRoleCreate,
    current_role=Depends(get_current_user),
    service: UserRoleService = Depends(get_user_role_service),
):
    return service.create_user_role(user_role_data)


@router.get(
    "",
    response_model=list[UserRoleResponse],
    status_code=status.HTTP_200_OK,
)
def get_all_user_roles(
    current_role=Depends(get_current_user),
    service: UserRoleService = Depends(get_user_role_service),
):
    return service.get_all_user_roles()


@router.get(
    "/{user_role_id}",
    response_model=UserRoleResponse,
    status_code=status.HTTP_200_OK,
)
def get_user_role_by_id(
    user_role_id: UUID,
    current_role=Depends(get_current_user),
    service: UserRoleService = Depends(get_user_role_service),
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
    current_role=Depends(get_current_user),
    service: UserRoleService = Depends(get_user_role_service),
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
    current_role=Depends(get_current_user),
    service: UserRoleService = Depends(get_user_role_service),
):
    service.delete_user_role(user_role_id)
