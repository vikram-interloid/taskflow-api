from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.repositories.cache_repository import CacheRepository

from app.api.schemas.query_schema import UserTaskQueryParams

from app.api.models.users_model import User
from app.api.core.authorization import can_access_user_task
from app.api.models.user_task import UserTask
from app.api.repositories.task_repository import TaskRepository
from app.api.repositories.user_repository import UserRepository
from app.api.repositories.user_task_repository import UserTaskRepository
from app.api.schemas.user_task_schema import UserTaskCreate, UserTaskUpdate


class UserTaskService:
    def __init__(self, db: Session):
        self.user_task_repository = UserTaskRepository(db)
        self.user_repository = UserRepository(db)
        self.task_repository = TaskRepository(db)
        self.cache_repository = CacheRepository()

    def create_user_task(
        self,
        user_task_data: UserTaskCreate,
        current_user: User,
    ) -> UserTask:
        
        user = self.user_repository.get_user_by_id(user_task_data.user_id)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        task = self.task_repository.get_task_by_id(user_task_data.task_id)
        
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        
        existing = self.user_task_repository.get_user_task(
            user_task_data.user_id,
            user_task_data.task_id,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Task already assigned to this user",
            )

        user_task = UserTask(
            task_id = user_task_data.task_id,
            user_id = user_task_data.user_id,
            due_at = user_task_data.due_at,
            created_by = current_user.user_id,
            status = "pending",
        )

        user_task = self.user_task_repository.create_user_task(user_task)

        self.cache_repository.delete_pattern(
            "taskflow:cache:user_tasks*"
        )

        return user_task
        
        

    def get_user_task_by_id(
        self,
        user_task_id: UUID,
        current_user: User,
    ):

        cache_key = f"taskflow:cache:user_task:{user_task_id}"

        cached_user_task = self.cache_repository.get(cache_key)

        if cached_user_task is not None:
            return cached_user_task

        user_task = self.user_task_repository.get_user_task_by_id(
            user_task_id
        )

        if user_task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User task not found",
            )
            
        can_access_user_task(current_user, user_task)

        user_task_data = {
            "id": str(user_task.id),
            "task_id": str(user_task.task_id),
            "user_id": str(user_task.user_id),
            "created_by": str(user_task.created_by),
            "status": user_task.status.value,
            "due_at": user_task.due_at.isoformat() if user_task.due_at else None,
            "completed_at": (
                user_task.completed_at.isoformat()
                if user_task.completed_at
                else None
            ),
            "created_at": user_task.created_at.isoformat()
        }

        self.cache_repository.set(
            key=cache_key,
            value=user_task_data,
            expire=300,
        )

        return user_task_data
    
    

    def get_all_user_tasks(
        self,
        query: UserTaskQueryParams,
    ):

        cache_key = (
            f"taskflow:cache:user_tasks:"
            f"page={query.page}:"
            f"limit={query.limit}:"
            f"user={query.user_id}:"
            f"task={query.task_id}:"
            f"status={query.status}:"
            f"sort={query.sort_by}:"
            f"order={query.order}:"
            f"search={query.search}"
        )

        cached_user_tasks = self.cache_repository.get(cache_key)

        if cached_user_tasks is not None:
            return cached_user_tasks

        user_tasks = self.user_task_repository.get_all_user_tasks(query)

        user_task_list = [
            {
                "id": str(item.id),
                "task_id": str(item.task_id),
                "user_id": str(item.user_id),
                "created_by": str(item.created_by),
                "status": item.status.value,
                "due_at": item.due_at.isoformat() if item.due_at else None,
                "completed_at": (
                    item.completed_at.isoformat()
                    if item.completed_at
                    else None
                ),
                "created_at": item.created_at.isoformat(),
            }
            for item in user_tasks
        ]

        self.cache_repository.set(
            key=cache_key,
            value=user_task_list,
            expire=300,
        )

        return user_task_list
        
    

    def update_user_task(
        self,
        user_task_id: UUID,
        user_task_data: UserTaskUpdate,
        current_user: User,
    ) -> UserTask:
        
        user_task = self.user_task_repository.get_user_task_by_id(user_task_id)

        if user_task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User task not found",
            )
            
        can_access_user_task(current_user, user_task)

        update_data = user_task_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(user_task, key, value)

        user_task = self.user_task_repository.update_user_task(user_task)

        self.cache_repository.delete(
            f"taskflow:cache:user_task:{user_task.id}"
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:user_tasks*"
        )

        return user_task
    
    

    def delete_user_task(
        self,
        user_task_id: UUID,
        current_user: User,
    ) -> None:
        
        user_task = self.user_task_repository.get_user_task_by_id(user_task_id)

        if user_task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User task not found",
            )
            
        can_access_user_task(current_user, user_task)

        user_task_id = user_task.id

        self.user_task_repository.delete_user_task(user_task)

        self.cache_repository.delete(
            f"taskflow:cache:user_task:{user_task_id}"
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:user_tasks*"
        )
        
