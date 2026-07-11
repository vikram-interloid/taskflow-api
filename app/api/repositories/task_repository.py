from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.models.task_model import Task
from app.api.repositories.base_repository import BaseRepository
from app.api.schemas.query_schema import TaskQueryParams


class TaskRepository(BaseRepository):
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

    def get_all_tasks(
        self,
        query: TaskQueryParams,
    ):

        stmt = select(Task)

        filters = {
            "created_by": Task.created_by,
        }

        stmt = self.apply_filters(
            stmt=stmt,
            filters=filters,
            query=query,
        )

        stmt = self.apply_search(
            stmt=stmt,
            search=query.search,
            columns=[
                Task.task_name,
                Task.task_desc,
            ],
        )

        sortable_columns = {
            "task_name": Task.task_name,
            "created_at": Task.created_at,
        }

        stmt = self.apply_sort(
            stmt=stmt,
            sortable_columns=sortable_columns,
            sort_by=query.sort_by,
            order=query.order,
        )

        stmt = self.apply_pagination(
            stmt=stmt,
            page=query.page,
            limit=query.limit,
        )

        result = self.db.execute(stmt)

        return result.scalars().all()

    
    def update_task(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return task


    def delete_task(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()
        
        