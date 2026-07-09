from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.models.user_task import UserTask
from app.api.repositories.base_repository import BaseRepository
from app.api.schemas.query_schema import UserTaskQueryParams

class UserTaskRepository(BaseRepository):
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
        
    def get_all_user_tasks(
        self,
        query: UserTaskQueryParams,
    ):

        stmt = select(UserTask)

        filters = {
            "user_id": UserTask.user_id,
            "task_id": UserTask.task_id,
            "created_by": UserTask.created_by,
            "status": UserTask.status,
        }

        stmt = self.apply_filters(
            stmt=stmt,
            filters=filters,
            query=query,
        )


        stmt = self.apply_sort(
            stmt=stmt,
            sortable_columns={
                "status": UserTask.status,
                "due_at": UserTask.due_at,
                "created_at": UserTask.created_at,
            },
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
        
    
    def get_user_tasks_by_user_id(
        self,
        user_id: UUID,
    ):
        stmt = select(UserTask).where(
            UserTask.user_id == user_id
        )
        result = self.db.execute(stmt)

        return result.scalars().all()
    
    
    def get_user_tasks_by_creator(
        self,
        created_by: UUID,
    ):
        stmt = select(UserTask).where(
            UserTask.created_by == created_by
        )
        result = self.db.execute(stmt)

        return result.scalars().all()

