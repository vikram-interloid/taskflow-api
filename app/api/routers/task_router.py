from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.core.dependencies import get_current_user
from app.api.database.db_config import get_db
from app.api.core.rbac import require_roles
from app.api.enums.roles import RoleName
from app.api.models.users_model import User
from app.api.schemas.query_schema import TaskQueryParams
from app.api.schemas.pagination_schema import PaginatedResponse
from app.api.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
from app.api.services.task_service import TaskService

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


def get_task_service(
    db: Session = Depends(get_db),
) -> TaskService:
    return TaskService(db)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(
        require_roles([
            RoleName.ADMIN,
            RoleName.MANAGER,
        ])
    ),
    service: TaskService = Depends(get_task_service),
):
    return service.create_task(task_data,current_user)


@router.get(
    "",
    response_model= PaginatedResponse[TaskResponse],
    status_code=status.HTTP_200_OK,
)
def get_all_tasks(
    query: TaskQueryParams = Depends(),
    current_user: User = Depends(
        get_current_user
    ),
    service: TaskService = Depends(get_task_service),
):
    
    return service.get_all_tasks(query, current_user)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
def get_task_by_id(
    task_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    service: TaskService = Depends(get_task_service),
):
    return service.get_task_by_id(task_id, current_user)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(
        require_roles([
            RoleName.ADMIN,
            RoleName.MANAGER,
        ])
    ),
    service: TaskService = Depends(get_task_service),
):
    return service.update_task(task_id, task_data, current_user)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: UUID,
    current_user: User = Depends(
        require_roles([
            RoleName.ADMIN,
            RoleName.MANAGER,
        ])
    ),
    service: TaskService = Depends(get_task_service),
):
    service.delete_task(
        task_id=task_id,
        current_user=current_user,
    )
    
    