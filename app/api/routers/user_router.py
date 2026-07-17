from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.core.dependencies import get_current_user
from app.api.core.rbac import require_roles
from app.api.database.db_config import get_db
from app.api.enums.roles import RoleName
from app.api.models.users_model import User
from app.api.schemas.pagination_schema import PaginatedResponse
from app.api.schemas.query_schema import UserQueryParams
from app.api.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.api.services.error_service import (
    CREATE_RESPONSES,
    PROTECTED_RESPONSES,
    RESOURCE_RESPONSES,
)
from app.api.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(
    db: Session = Depends(get_db),
) -> UserService:
    return UserService(db)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses=CREATE_RESPONSES,
)
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_roles([RoleName.ADMIN])),
    service: UserService = Depends(get_user_service),
):
    return service.create_user(user_data)


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    responses=PROTECTED_RESPONSES,
)
def get_all_users(
    query: UserQueryParams = Depends(),
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return service.get_all_users(query, current_user)


@router.get(
    "/{id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses=RESOURCE_RESPONSES,
)
def get_user_by_id(
    id: UUID,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return service.get_user_by_id(id, current_user)


@router.patch(
    "/{id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses=RESOURCE_RESPONSES,
)
def update_user(
    id: UUID,
    user_data: UserUpdate,
    current_user: User = Depends(require_roles([RoleName.ADMIN])),
    service: UserService = Depends(get_user_service),
):

    return service.update_user(
        user_id=id,
        userdata=user_data,
        current_user=current_user,
    )


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, responses=RESOURCE_RESPONSES
)
def delete_user(
    id: UUID,
    current_user: User = Depends(require_roles([RoleName.ADMIN])),
    service: UserService = Depends(get_user_service),
):
    service.delete_user(
        user_id=id,
        current_user=current_user,
    )
