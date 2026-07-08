from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.models.user_task import UserTask

class UserTaskRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create_user_task(self, user_task: UserTask) -> UserTask:
        self.db.add(user_task)
        self.db.commit()
        self.db.refresh(user_task)
        return user_task
    
    def get_user_task_by_id(
        self,
        user_task_id: UUID,
    ) -> UserTask | None:
        stmt = select(UserTask).where(
            UserTask.id == user_task_id
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_user_task(
            self,
            user_id: UUID,
            task_id: UUID,
        ) -> UserTask | None:
            stmt = (
                select(UserTask)
                .where(UserTask.user_id == user_id)
                .where(UserTask.task_id == task_id)
            )
            result = self.db.execute(stmt)
            return result.scalar_one_or_none()
        
    def get_all_user_tasks(self):
        stmt = select(UserTask)
        result = self.db.execute(stmt)
        return result.scalars().all()

    def update_user_task(
        self,
        user_task: UserTask,
    ) -> UserTask:
        self.db.commit()
        self.db.refresh(user_task)
        return user_task

    def delete_user_task(
        self,
        user_task: UserTask,
    ) -> None:
        self.db.delete(user_task)
        self.db.commit()

