from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.schemas.query_schema import UserTaskQueryParams

from app.api.models.users_model import User
from app.api.core.dependencies import get_current_user

from app.api.database.db_config import get_db
from app.api.schemas.user_task_schema import UserTaskCreate, UserTaskResponse,UserTaskUpdate
from app.api.services.user_task_service import UserTaskService

router = APIRouter(
    prefix="/user-tasks",
    tags=["User Tasks"],
)


def get_user_task_service(db: Session = Depends(get_db)) -> UserTaskService:
    return UserTaskService(db)


@router.post(
    "",
    response_model=UserTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_task(
    user_task_data: UserTaskCreate,
    current_user: User = Depends(get_current_user),
    service: UserTaskService = Depends(get_user_task_service),
):
    return service.create_user_task(
        user_task_data,
        current_user,
    )


@router.get(
    "",
    response_model=list[UserTaskResponse],
    status_code=status.HTTP_200_OK,
)
def get_all_user_tasks(
    query: UserTaskQueryParams = Depends(),
    current_user: User = Depends(get_current_user),
    service: UserTaskService = Depends(get_user_task_service),
):
    return service.get_all_user_tasks(query)


@router.get(
    "/{user_task_id}",
    response_model=UserTaskResponse,
    status_code=status.HTTP_200_OK,
)
def get_user_task_by_id(
    user_task_id: UUID,
    current_role=Depends(get_current_user),
    service: UserTaskService = Depends(get_user_task_service),
):
    return service.get_user_task_by_id(user_task_id,current_role)


@router.patch(
    "/{user_task_id}",
    response_model=UserTaskResponse,
    status_code=status.HTTP_200_OK,
)
def update_user_task(
    user_task_id: UUID,
    user_task_data: UserTaskUpdate,
    current_role=Depends(get_current_user),
    service: UserTaskService = Depends(get_user_task_service),
):
    return service.update_user_task(
        user_task_id,
        user_task_data,
        current_role
    )


@router.delete(
    "/{user_task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user_task(
    user_task_id: UUID,
    current_role=Depends(get_current_user),
    service: UserTaskService = Depends(get_user_task_service),
):
    service.delete_user_task(user_task_id,current_role)
    