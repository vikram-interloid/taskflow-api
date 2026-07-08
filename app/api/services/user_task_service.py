from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

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

    def create_user_task(
        self,
        user_task_data: UserTaskCreate,
    ) -> UserTask:
        
        user = self.user_repository.get_user_by_id(
            user_task_data.user_id
        )
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        task = self.task_repository.get_task_by_id(
            user_task_data.task_id
        )
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        creator = self.user_repository.get_user_by_id(
            user_task_data.created_by
        )
        if creator is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Created by user not found",
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
            task_id=user_task_data.task_id,
            user_id=user_task_data.user_id,
            due_at=user_task_data.due_at,
            created_by=user_task_data.created_by,
            status="pending",
        )

        return self.user_task_repository.create_user_task(
            user_task
        )
        
        

    def get_user_task_by_id(
        self,
        user_task_id: UUID,
    ) -> UserTask:
        user_task = self.user_task_repository.get_user_task_by_id(user_task_id)

        if user_task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User task not found",
            )
            
        return user_task
    
    

    def get_all_user_tasks(self) -> list[UserTask]:
        return self.user_task_repository.get_all_user_tasks()
    
    

    def update_user_task(
        self,
        user_task_id: UUID,
        user_task_data: UserTaskUpdate,
    ) -> UserTask:
        
        user_task = self.user_task_repository.get_user_task_by_id(user_task_id)

        if user_task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User task not found",
            )

        update_data = user_task_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(user_task, key, value)

        return self.user_task_repository.update_user_task(user_task)
    
    

    def delete_user_task(
        self,
        user_task_id: UUID,
    ) -> None:
        
        user_task = self.user_task_repository.get_user_task_by_id(user_task_id)

        if user_task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User task not found",
            )

        self.user_task_repository.delete_user_task(user_task)
        
