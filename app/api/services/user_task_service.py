from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.core.authorization import can_access_user_task, is_admin
from app.api.core.logging import get_logger
from app.api.enums.roles import RoleName
from app.api.models.user_task import UserTask
from app.api.models.users_model import User
from app.api.repositories.cache_repository import CacheRepository
from app.api.repositories.task_repository import TaskRepository
from app.api.repositories.user_repository import UserRepository
from app.api.repositories.user_role_repository import UserRoleRepository
from app.api.repositories.user_task_repository import UserTaskRepository
from app.api.schemas.query_schema import UserTaskQueryParams
from app.api.schemas.user_task_schema import UserTaskCreate, UserTaskUpdate

logger = get_logger(__name__)

class UserTaskService:
    def __init__(self, db: Session):
        self.user_task_repository = UserTaskRepository(db)
        self.user_repository = UserRepository(db)
        self.task_repository = TaskRepository(db)
        self.user_role_repository = UserRoleRepository(db)
        self.cache_repository = CacheRepository()

    def create_user_task(
        self,
        user_task_data: UserTaskCreate,
        current_user: User,
    ) -> UserTask:

        logger.info(
            "Assigning task %s to user %s",
            user_task_data.task_id,
            user_task_data.user_id,
        )

        user = self.user_repository.get_user_by_id(
            user_task_data.user_id,
        )

        if user is None:
            logger.warning(
                "User %s not found",
                user_task_data.user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        task = self.task_repository.get_task_by_id(
            user_task_data.task_id,
        )

        if task is None:
            logger.warning(
                "Task %s not found",
                user_task_data.task_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        if not is_admin(current_user):
            if task.created_by != current_user.user_id:
                logger.warning(
                    "Manager %s attempted to assign task %s created by %s",
                    current_user.user_id,
                    task.task_id,
                    task.created_by,
                )

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Managers can only assign tasks they created",
                )
                
        if not is_admin(current_user):
            target_user_roles = (
                self.user_role_repository.get_roles_by_user_id(
                    user.user_id,
                )
            )

            target_is_admin = any(
                role.role_name == RoleName.ADMIN
                for role in target_user_roles
            )

            if target_is_admin:
                logger.warning(
                    "Manager %s attempted to assign a task to admin %s",
                    current_user.user_id,
                    user.user_id,
                )

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Managers cannot assign tasks to admins",
                )

        existing = self.user_task_repository.get_user_task(
            user_task_data.user_id,
            user_task_data.task_id,
        )

        if existing:
            logger.warning(
                "Task %s is already assigned to user %s",
                user_task_data.task_id,
                user_task_data.user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Task already assigned to this user",
            )

        user_task = UserTask(
            task_id=user_task_data.task_id,
            user_id=user_task_data.user_id,
            due_at=user_task_data.due_at,
            created_by=current_user.user_id,
            status="pending",
        )

        user_task = self.user_task_repository.create_user_task(
            user_task,
        )

        logger.info(
            "Assigned task %s to user %s",
            user_task.task_id,
            user_task.user_id,
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:user_tasks*",
        )

        logger.info(
            "Invalidated cache pattern 'taskflow:cache:user_tasks*'",
        )

        return user_task
        
        

    def get_user_task_by_id(
        self,
        user_task_id: UUID,
        current_user: User,
    ):

        logger.info(
            "Fetching user-task %s",
            user_task_id,
        )

        user_task = self.user_task_repository.get_user_task_by_id(
            user_task_id,
        )

        if user_task is None:
            logger.warning(
                "User-task %s not found",
                user_task_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User task not found",
            )

        can_access_user_task(
            current_user,
            user_task,
        )

        cache_key = f"taskflow:cache:user_task:{user_task_id}"

        logger.info(
            "Checking cache '%s'",
            cache_key,
        )

        cached_user_task = self.cache_repository.get(
            cache_key,
        )

        if cached_user_task is not None:
            logger.info(
                "Cache HIT '%s'",
                cache_key,
            )

            return cached_user_task

        logger.info(
            "Cache MISS '%s'",
            cache_key,
        )

        logger.info(
            "Retrieved user-task %s from database",
            user_task.id,
        )

        user_task_data = {
            "id": str(user_task.id),
            "task_id": str(user_task.task_id),
            "user_id": str(user_task.user_id),
            "created_by": str(user_task.created_by),
            "status": user_task.status.value,
            "due_at": (
                user_task.due_at.isoformat()
                if user_task.due_at
                else None
            ),
            "completed_at": (
                user_task.completed_at.isoformat()
                if user_task.completed_at
                else None
            ),
            "created_at": user_task.created_at.isoformat(),
        }

        self.cache_repository.set(
            key=cache_key,
            value=user_task_data,
            expire=300,
        )

        logger.info(
            "Cached user-task %s for 300 seconds",
            user_task.id,
        )

        return user_task_data
        
    

    def get_all_user_tasks(
        self,
        query: UserTaskQueryParams,
        current_user: User,
    ) -> dict:

        roles = self.user_role_repository.get_roles_by_user_id(
            current_user.user_id,
        )

        is_admin = any(
            role.role_name == RoleName.ADMIN
            for role in roles
        )

        if not is_admin:
            query.user_id = current_user.user_id

        cache_key = (
            f"taskflow:cache:user_tasks:"
            f"admin={is_admin}:"
            f"user={current_user.user_id}:"
            f"page={query.page}:"
            f"limit={query.limit}:"
            f"user_filter={query.user_id}:"
            f"task={query.task_id}:"
            f"created_by={query.created_by}:"
            f"status={query.status}:"
            f"sort={query.sort_by}:"
            f"order={query.order}:"
            f"search={query.search}"
        )

        logger.info(
            "Checking cache '%s'",
            cache_key,
        )

        cached_response = self.cache_repository.get(
            cache_key,
        )

        if cached_response is not None:
            logger.info(
                "Cache HIT '%s'",
                cache_key,
            )

            return cached_response

        logger.info(
            "Cache MISS '%s'",
            cache_key,
        )

        user_tasks, total = self.user_task_repository.get_all_user_tasks(
            query,
        )

        logger.info(
            "Retrieved %d user-task records from database",
            len(user_tasks),
        )

        user_task_list = [
            {
                "id": str(item.id),
                "task_id": str(item.task_id),
                "user_id": str(item.user_id),
                "created_by": str(item.created_by),
                "status": item.status.value,
                "due_at": (
                    item.due_at.isoformat()
                    if item.due_at
                    else None
                ),
                "completed_at": (
                    item.completed_at.isoformat()
                    if item.completed_at
                    else None
                ),
                "created_at": item.created_at.isoformat(),
            }
            for item in user_tasks
        ]

        response = {
            "page": query.page,
            "limit": query.limit,
            "total": total,
            "data": user_task_list,
        }

        self.cache_repository.set(
            key=cache_key,
            value=response,
            expire=300,
        )

        logger.info(
            "Cached page %d containing %d user-task records (total=%d)",
            query.page,
            len(user_task_list),
            total,
        )

        return response
            
    

    def update_user_task(
        self,
        user_task_id: UUID,
        user_task_data: UserTaskUpdate,
        current_user: User,
    ) -> UserTask:

        logger.info(
            "Updating user-task %s",
            user_task_id,
        )

        user_task = self.user_task_repository.get_user_task_by_id(
            user_task_id,
        )

        if user_task is None:
            logger.warning(
                "User-task %s not found",
                user_task_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User task not found",
            )

        can_access_user_task(
            current_user,
            user_task,
        )

        update_data = user_task_data.model_dump(
            exclude_unset=True,
        )

        for key, value in update_data.items():
            setattr(
                user_task,
                key,
                value,
            )

        user_task = self.user_task_repository.update_user_task(
            user_task,
        )

        logger.info(
            "Updated user-task %s",
            user_task.id,
        )

        if update_data:
            logger.info(
                "Updated fields: %s",
                ", ".join(update_data.keys()),
            )

        self.cache_repository.delete(
            f"taskflow:cache:user_task:{user_task.id}",
        )

        logger.info(
            "Invalidated cache 'taskflow:cache:user_task:%s'",
            user_task.id,
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:user_tasks*",
        )

        logger.info(
            "Invalidated cache pattern 'taskflow:cache:user_tasks*'",
        )

        return user_task
    
    

    def delete_user_task(
        self,
        user_task_id: UUID,
        current_user: User,
    ) -> None:

        logger.info(
            "Deleting user-task %s",
            user_task_id,
        )

        user_task = self.user_task_repository.get_user_task_by_id(
            user_task_id,
        )

        if user_task is None:
            logger.warning(
                "User-task %s not found",
                user_task_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User task not found",
            )

        can_access_user_task(
            current_user,
            user_task,
        )

        self.user_task_repository.delete_user_task(
            user_task,
        )

        logger.info(
            "Deleted user-task %s",
            user_task.id,
        )

        self.cache_repository.delete(
            f"taskflow:cache:user_task:{user_task.id}",
        )

        logger.info(
            "Invalidated cache 'taskflow:cache:user_task:%s'",
            user_task.id,
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:user_tasks*",
        )

        logger.info(
            "Invalidated cache pattern 'taskflow:cache:user_tasks*'",
        )
        
