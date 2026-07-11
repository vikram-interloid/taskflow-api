from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.core.dependencies import get_current_user
from app.api.database.db_config import get_db
from app.api.models.users_model import User
from app.api.schemas.query_schema import UserQueryParams
from app.api.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.api.services.user_service import UserService

router = APIRouter(
    prefix = '/users',
    tags = ["Users"]
)

def get_user_service(db: Session = Depends(get_db),) -> UserService:
    return UserService(db)


@router.post(
    '',
    response_model = UserResponse,
    status_code = status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    return service.create_user(user_data)

@router.get(
    '',
    response_model = list[UserResponse],
    status_code = status.HTTP_200_OK,
)
def get_all_users(
    query: UserQueryParams = Depends(),
    current_user=Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return service.get_all_users(query)


@router.get(
    '/{user_id}',
    response_model = UserResponse,
    status_code = status.HTTP_200_OK,
)
def get_user_by_id(
    user_id: UUID,
    current_user=Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return service.get_user_by_id(user_id)


@router.patch(
    '/{user_id}',
    response_model = UserResponse,
    status_code = status.HTTP_200_OK,
)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    
    return service.update_user(
        user_id = user_id,
        userdata = user_data,
        current_user = current_user,
    )


@router.delete(
    '/{user_id}',
    status_code = status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    service.delete_user(
        user_id = user_id,
        current_user = current_user,
    )

