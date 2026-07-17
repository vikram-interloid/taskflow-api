from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.core.authorization import can_access_task, is_admin, is_manager
from app.api.core.logging import get_logger
from app.api.enums.roles import RoleName
from app.api.models.task_model import Task
from app.api.models.users_model import User
from app.api.repositories.cache_repository import CacheRepository
from app.api.repositories.task_repository import TaskRepository
from app.api.repositories.user_repository import UserRepository
from app.api.repositories.user_role_repository import UserRoleRepository
from app.api.schemas.query_schema import TaskQueryParams
from app.api.schemas.task_schema import TaskCreate, TaskUpdate

logger = get_logger(__name__)


class TaskService:
    def __init__(self, db: Session):
        self.task_repository = TaskRepository(db)
        self.user_repository = UserRepository(db)
        self.user_role_repository = UserRoleRepository(db)
        self.cache_repository = CacheRepository()

    def create_task(
        self,
        taskdata: TaskCreate,
        current_user: User,
    ) -> Task:

        logger.info(
            "Creating task '%s'",
            taskdata.name,
        )

        user = self.user_repository.get_user_by_id(
            current_user.user_id,
        )

        if user is None:
            logger.warning(
                "User %s not found while creating task",
                current_user.user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        task = Task(
            name=taskdata.name,
            desc=taskdata.desc,
            created_by=current_user.user_id,
        )

        task = self.task_repository.create_task(
            task,
        )

        logger.info(
            "Task %s created successfully",
            task.task_id,
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:tasks*",
        )

        logger.info(
            "Invalidated cache pattern 'taskflow:cache:tasks*'",
        )

        return task

    def get_task_by_id(self, task_id: UUID, current_user: User) -> dict:

        logger.info(
            "Fetching task %s",
            task_id,
        )

        cache_key = f"taskflow:cache:task:{task_id}"

        logger.info(
            "Checking cache '%s'",
            cache_key,
        )

        cached_task = self.cache_repository.get(
            cache_key,
        )

        if cached_task is not None:
            logger.info(
                "Cache HIT '%s'",
                cache_key,
            )

            return cached_task

        logger.info(
            "Cache MISS '%s'",
            cache_key,
        )

        task = self.task_repository.get_task_by_id(
            task_id,
        )

        if task is None:
            logger.warning(
                "Task %s not found",
                task_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        can_access_task(
            current_user,
            task,
        )

        logger.info(
            "Retrieved task '%s' (%s) from database",
            task.name,
            task.task_id,
        )

        task_data = {
            "task_id": str(task.task_id),
            "name": task.name,
            "desc": task.desc,
            "created_by": str(task.created_by),
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

        self.cache_repository.set(
            key=cache_key,
            value=task_data,
            expire=300,
        )

        logger.info(
            "Cached task %s for 300 seconds",
            task.task_id,
        )

        return task_data

    def get_all_tasks(
        self,
        query: TaskQueryParams,
        current_user: User,
    ) -> dict:

        if not is_admin(current_user):
            query.created_by = current_user.user_id

        cache_key = (
            f"taskflow:cache:tasks:"
            f"admin={is_admin(current_user)}:"
            f"manager={is_manager(current_user)}:"
            f"user={current_user.user_id}:"
            f"created_by={query.created_by}:"
            f"page={query.page}:"
            f"limit={query.limit}:"
            f"search={query.search}:"
            f"sort={query.sort_by}:"
            f"order={query.order}"
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

        tasks, total = self.task_repository.get_all_tasks(
            query,
        )

        logger.info(
            "Retrieved %d tasks from database",
            len(tasks),
        )

        task_list = [
            {
                "task_id": str(task.task_id),
                "name": task.name,
                "desc": task.desc,
                "created_by": str(task.created_by),
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            }
            for task in tasks
        ]

        response = {
            "page": query.page,
            "limit": query.limit,
            "total": total,
            "data": task_list,
        }

        self.cache_repository.set(
            key=cache_key,
            value=response,
            expire=300,
        )

        logger.info(
            "Cached page %d containing %d tasks (total=%d)",
            query.page,
            len(task_list),
            total,
        )

        return response

    def update_task(
        self,
        task_id: UUID,
        taskdata: TaskUpdate,
        current_user: User,
    ) -> Task:

        logger.info(
            "Updating task %s",
            task_id,
        )

        task = self.task_repository.get_task_by_id(
            task_id,
        )

        if task is None:
            logger.warning(
                "Task %s not found",
                task_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        roles = self.user_role_repository.get_roles_by_user_id(
            current_user.user_id,
        )

        is_admin = any(role.role_name == RoleName.ADMIN for role in roles)

        if task.created_by != current_user.user_id and not is_admin:
            logger.warning(
                "User %s attempted to update task %s owned by %s",
                current_user.user_id,
                task_id,
                task.created_by,
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to update this task",
            )

        update_data = taskdata.model_dump(
            exclude_unset=True,
        )

        for key, value in update_data.items():
            setattr(
                task,
                key,
                value,
            )

        task = self.task_repository.update_task(
            task,
        )

        logger.info(
            "Updated task '%s' (%s)",
            task.name,
            task.task_id,
        )

        if update_data:
            logger.info(
                "Updated fields: %s",
                ", ".join(update_data.keys()),
            )

        self.cache_repository.delete(
            f"taskflow:cache:task:{task.task_id}",
        )

        logger.info(
            "Invalidated cache 'taskflow:cache:task:%s'",
            task.task_id,
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:tasks*",
        )

        logger.info(
            "Invalidated cache pattern 'taskflow:cache:tasks*'",
        )

        return task

    def delete_task(
        self,
        task_id: UUID,
        current_user: User,
    ) -> None:

        logger.info(
            "Deleting task %s",
            task_id,
        )

        task = self.task_repository.get_task_by_id(
            task_id,
        )

        if task is None:
            logger.warning(
                "Task %s not found",
                task_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        roles = self.user_role_repository.get_roles_by_user_id(
            current_user.user_id,
        )

        is_admin = any(role.role_name == RoleName.ADMIN for role in roles)

        if task.created_by != current_user.user_id and not is_admin:
            logger.warning(
                "User %s attempted to update task %s owned by %s",
                current_user.user_id,
                task_id,
                task.created_by,
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to delete this task",
            )

        self.task_repository.delete_task(
            task,
        )

        logger.info(
            "Deleted task '%s' (%s)",
            task.name,
            task.task_id,
        )

        self.cache_repository.delete(
            f"taskflow:cache:task:{task_id}",
        )

        logger.info(
            "Invalidated cache 'taskflow:cache:task:%s'",
            task_id,
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:tasks*",
        )

        logger.info(
            "Invalidated cache pattern 'taskflow:cache:tasks*'",
        )
