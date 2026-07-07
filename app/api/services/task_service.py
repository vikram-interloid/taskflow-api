from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.models.task_model import Task
from app.api.repositories.task_repository import TaskRepository
from app.api.repositories.user_repository import UserRepository
from app.api.schemas.task_schema import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, db: Session):
        self.task_repository = TaskRepository(db)
        self.user_repository = UserRepository(db)

    def create_task(self, taskdata: TaskCreate) -> Task:
        user = self.user_repository.get_user_by_id(taskdata.created_by)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        task = Task(
            task_name=taskdata.task_name,
            task_desc=taskdata.task_desc,
            created_by=taskdata.created_by,
        )

        return self.task_repository.create_task(task)

    def get_task_by_id(self, task_id: UUID) -> Task:
        task = self.task_repository.get_task_by_id(task_id)

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return task
    

    def get_all_tasks(self) -> list[Task]:
        return self.task_repository.get_all_tasks()
    
    

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

        return self.task_repository.update_task(task)
    
    

    def delete_task(self, task_id: UUID) -> None:
        task = self.task_repository.get_task_by_id(task_id)

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        self.task_repository.delete_task(task)
        
        