from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.database.db_config import get_db
from app.api.schemas.task_schema import TaskCreate,TaskResponse,TaskUpdate
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
    service: TaskService = Depends(get_task_service),
):
    return service.create_task(task_data)


@router.get(
    "",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
)
def get_all_tasks(
    service: TaskService = Depends(get_task_service),
):
    return service.get_all_tasks()


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
def get_task_by_id(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
):
    return service.get_task_by_id(task_id)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
):
    return service.update_task(task_id, task_data)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
):
    service.delete_task(task_id)