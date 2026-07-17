from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.core.dependencies import get_current_user
from app.api.core.rbac import require_roles
from app.api.database.db_config import get_db
from app.api.enums.roles import RoleName
from app.api.models.users_model import User
from app.api.schemas.pagination_schema import PaginatedResponse
from app.api.schemas.query_schema import UserTaskQueryParams
from app.api.schemas.user_task_schema import (
    UserTaskCreate,
    UserTaskResponse,
    UserTaskUpdate,
)
from app.api.services.error_service import (
    CREATE_RESOURCE_RESPONSES,
    RESOURCE_RESPONSES,
)
from app.api.services.user_task_service import UserTaskService


router = APIRouter(
    prefix="/tasks/{id}/assignees",
    tags=["Task Assignments"],
)


def get_user_task_service(
    db: Session = Depends(get_db),
) -> UserTaskService:
    return UserTaskService(db)


@router.post(
    "",
    response_model=UserTaskResponse,
    status_code=status.HTTP_201_CREATED,
    responses=CREATE_RESOURCE_RESPONSES,
)
def assign_task(
    task_id: UUID,
    request: UserTaskCreate,
    current_user: User = Depends(
        require_roles(
            [
                RoleName.ADMIN,
                RoleName.MANAGER,
            ]
        )
    ),
    service: UserTaskService = Depends(
        get_user_task_service,
    ),
):
    return service.create_user_task(
        task_id=task_id,
        user_task_data=request,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=PaginatedResponse[UserTaskResponse],
    status_code=status.HTTP_200_OK,
    responses=RESOURCE_RESPONSES,
)
def get_task_assignees(
    task_id: UUID,
    query: UserTaskQueryParams = Depends(),
    current_user: User = Depends(
        get_current_user,
    ),
    service: UserTaskService = Depends(
        get_user_task_service,
    ),
):
    return service.get_task_assignees(
        task_id=task_id,
        query=query,
        current_user=current_user,
    )


@router.get(
    "/{assignee_id}",
    response_model=UserTaskResponse,
    status_code=status.HTTP_200_OK,
    responses=RESOURCE_RESPONSES,
)
def get_task_assignee(
    id: UUID,
    assignee_id: UUID,
    current_user: User = Depends(
        get_current_user,
    ),
    service: UserTaskService = Depends(
        get_user_task_service,
    ),
):
    return service.get_task_assignee(
        task_id = id,
        user_id = assignee_id,
        current_user = current_user,
    )


@router.patch(
    "/{assignee_id}",
    response_model=UserTaskResponse,
    status_code=status.HTTP_200_OK,
    responses=RESOURCE_RESPONSES,
)
def update_task_assignment(
    id: UUID,
    assignee_id: UUID,
    user_task_data: UserTaskUpdate,
    current_user: User = Depends(
        get_current_user,
    ),
    service: UserTaskService = Depends(
        get_user_task_service,
    ),
):
    return service.update_user_task(
        task_id = id,
        user_id = assignee_id,
        user_task_data = user_task_data,
        current_user = current_user,
    )


@router.delete(
    "/{assignee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESOURCE_RESPONSES,
)
def remove_task_assignment(
    id: UUID,
    assignee_id: UUID,
    current_user: User = Depends(
        require_roles(
            [
                RoleName.ADMIN,
                RoleName.MANAGER,
            ]
        )
    ),
    service: UserTaskService = Depends(
        get_user_task_service,
    ),
):
    service.delete_user_task(
        task_id = id,
        user_id = assignee_id,
        current_user=current_user,
    )

    return None

