from typing import Dict
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.repositories.cache_repository import CacheRepository

from app.api.schemas.query_schema import TaskQueryParams

from app.api.models.users_model import User
from app.api.models.task_model import Task
from app.api.repositories.task_repository import TaskRepository
from app.api.repositories.user_repository import UserRepository
from app.api.schemas.task_schema import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, db: Session):
        self.task_repository = TaskRepository(db)
        self.user_repository = UserRepository(db)
        self.cache_repository = CacheRepository()

    def create_task(self, taskdata: TaskCreate,current_user: User) -> Task:
        user = self.user_repository.get_user_by_id(current_user.user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        task = Task(
            task_name=taskdata.task_name,
            task_desc=taskdata.task_desc,
            created_by=current_user.user_id,
        )

        task = self.task_repository.create_task(task)

        self.cache_repository.delete_pattern(
            "taskflow:cache:tasks*"
        )

        return task
            
    

    def get_task_by_id(self, task_id: UUID) -> Task | Dict:
        
        cache_key = f"taskflow:cache:task:{task_id}"

        cached_task = self.cache_repository.get(cache_key)

        if cached_task is not None:
            return cached_task
    
        task = self.task_repository.get_task_by_id(task_id)

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        task_data = {
            "task_id": str(task.task_id),
            "task_name": task.task_name,
            "task_desc": task.task_desc,
            "created_by": str(task.created_by),
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

        self.cache_repository.set(
            key=cache_key,
            value=task_data,
            expire=300,
        )

        return task_data
    

    def get_all_tasks(
        self,
        query: TaskQueryParams,
    ):

        cache_key = (
            f"taskflow:cache:tasks:"
            f"page={query.page}:"
            f"limit={query.limit}:"
            f"search={query.search}:"
            f"sort={query.sort_by}:"
            f"order={query.order}"
        )

        cached_tasks = self.cache_repository.get(cache_key)

        if cached_tasks is not None:
            return cached_tasks

        tasks = self.task_repository.get_all_tasks(query)

        task_list = [
            {
                "task_id": str(task.task_id),
                "task_name": task.task_name,
                "task_desc": task.task_desc,
                "created_by": str(task.created_by),
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            }
            for task in tasks
        ]

        self.cache_repository.set(
            key=cache_key,
            value=task_list,
            expire=300,
        )

        return task_list
    
    

    def update_task(
        self,
        task_id: UUID,
        taskdata: TaskUpdate,
    ) -> Task:
        task = self.task_repository.get_task_by_id(task_id)

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        update_data = taskdata.model_dump(exclude_unset=True)

        if "created_by" in update_data:
            user = self.user_repository.get_user_by_id(
                update_data["created_by"]
            )

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

        for key, value in update_data.items():
            setattr(task, key, value)

        task = self.task_repository.update_task(task)

        self.cache_repository.delete(
            f"taskflow:cache:task:{task.task_id}"
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:tasks*"
        )

        return task
    
    

    def delete_task(self, task_id: UUID) -> None:
        task = self.task_repository.get_task_by_id(task_id)

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        self.task_repository.delete_task(task)

        self.cache_repository.delete(
            f"taskflow:cache:task:{task_id}"
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:tasks*"
        )
        
        