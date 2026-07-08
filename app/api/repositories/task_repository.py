from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.models.task_model import Task

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create_task(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def get_task_by_id(self, task_id: UUID) -> Task | None:
        stmt = select(Task).where(Task.task_id == task_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_all_tasks(self):
        stmt = select(Task)
        result = self.db.execute(stmt)
        return result.scalars().all()

    
    def update_task(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return task


    def delete_task(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()
        