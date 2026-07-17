from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.core.authorization import can_access_user_task, is_admin
from app.api.core.logging import get_logger
from app.api.enums.roles import RoleName
from app.api.enums.task_status import TaskStatus
from app.api.models.user_task import UserTask
from app.api.models.users_model import User
from app.api.repositories.cache_repository import CacheRepository
from app.api.repositories.role_repository import RoleRepository
from app.api.repositories.task_repository import TaskRepository
from app.api.repositories.user_repository import UserRepository
from app.api.repositories.user_role_repository import UserRoleRepository
from app.api.repositories.user_task_repository import UserTaskRepository
from app.api.schemas.query_schema import UserTaskQueryParams
from app.api.schemas.user_task_schema import (
    UserTaskCreate,
    UserTaskUpdate,
)

logger = get_logger(__name__)

class UserTaskService:

    def __init__(
        self,
        db: Session,
    ):
        self.user_task_repository = UserTaskRepository(db)
        self.user_repository = UserRepository(db)
        self.task_repository = TaskRepository(db)
        self.user_role_repository = UserRoleRepository(db)
        self.role_repository = RoleRepository(db)
        self.cache_repository = CacheRepository()
        
    def create_user_task(
        self,
        task_id: UUID,
        user_task_data: UserTaskCreate,
        current_user: User,
    ) -> UserTask:

        logger.info(
            "Assigning task %s to user %s",
            task_id,
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

        if self.user_task_repository.user_task_exists(
            user_id=user.user_id,
            task_id=task_id,
        ):
            logger.warning(
                "Task %s is already assigned to user %s",
                task_id,
                user.user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Task already assigned to this user",
            )

        user_task = UserTask(
            task_id=task_id,
            user_id=user.user_id,
            due_at=user_task_data.due_at,
            created_by=current_user.user_id,
            status=TaskStatus.PENDING,
        )

        user_task = self.user_task_repository.create_user_task(
            user_task,
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:user_tasks*",
        )

        logger.info(
            "Assigned task %s to user %s",
            task_id,
            user.user_id,
        )

        return user_task
    
    def get_task_assignees(
        self,
        task_id: UUID,
        query: UserTaskQueryParams,
        current_user: User,
    ) -> dict:

        logger.info(
            "Fetching assignees for task %s",
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

        if (
            not is_admin(current_user)
            and task.created_by != current_user.user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )

        cache_key = (
            f"taskflow:cache:task_assignees:"
            f"{task_id}:"
            f"page={query.page}:"
            f"limit={query.limit}:"
            f"user={query.user_id}:"
            f"status={query.status}:"
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

        assignments, total = (
            self.user_task_repository.get_task_assignees(
                task_id=task_id,
                query=query,
            )
        )
        assignment_list = [
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
                "updated_at": item.updated_at.isoformat(),
            }
            for item in assignments
        ]

        response = {
            "page": query.page,
            "limit": query.limit,
            "total": total,
            "data": assignment_list,
        }

        self.cache_repository.set(
            key=cache_key,
            value=response,
            expire=300,
        )

        logger.info(
            "Cached assignees for task %s",
            task_id,
        )

        return response
    
    
    def get_task_assignee(
        self,
        task_id: UUID,
        user_id: UUID,
        current_user: User,
    ) -> UserTask:

        logger.info(
            "Fetching assignment of user %s for task %s",
            user_id,
            task_id,
        )

        assignment = self.user_task_repository.get_user_task(
            user_id=user_id,
            task_id=task_id,
        )

        if assignment is None:
            logger.warning(
                "Assignment not found",
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task assignment not found",
            )

        can_access_user_task(
            current_user,
            assignment,
        )

        cache_key = (
            f"taskflow:cache:task_assignment:"
            f"{task_id}:{user_id}"
        )

        logger.info(
            "Checking cache '%s'",
            cache_key,
        )

        cached_assignment = self.cache_repository.get(
            cache_key,
        )

        if cached_assignment is not None:
            logger.info(
                "Cache HIT '%s'",
                cache_key,
            )

            return cached_assignment

        logger.info(
            "Cache MISS '%s'",
            cache_key,
        )

        assignment_data = {
            "id": str(assignment.id),
            "task_id": str(assignment.task_id),
            "user_id": str(assignment.user_id),
            "created_by": str(assignment.created_by),
            "status": assignment.status.value,
            "due_at": (
                assignment.due_at.isoformat()
                if assignment.due_at
                else None
            ),
            "completed_at": (
                assignment.completed_at.isoformat()
                if assignment.completed_at
                else None
            ),
            "created_at": assignment.created_at.isoformat(),
            "updated_at": assignment.updated_at.isoformat(),
        }

        self.cache_repository.set(
            key=cache_key,
            value=assignment_data,
            expire=300,
        )

        logger.info(
            "Cached assignment for task %s and user %s",
            task_id,
            user_id,
        )

        return assignment_data
    
    def update_user_task(
        self,
        task_id: UUID,
        user_id: UUID,
        user_task_data: UserTaskUpdate,
        current_user: User,
    ) -> UserTask:

        logger.info(
            "Updating assignment of task %s for user %s",
            task_id,
            user_id,
        )

        user_task = self.user_task_repository.get_user_task(
            user_id=user_id,
            task_id=task_id,
        )

        if user_task is None:
            logger.warning(
                "Task assignment not found",
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task assignment not found",
            )

        can_access_user_task(
            current_user,
            user_task,
        )

        update_data = user_task_data.model_dump(
            exclude_unset=True,
        )

        if "status" in update_data:

            new_status = update_data.pop("status")

            current_status = user_task.status

            allowed_transitions = {
                TaskStatus.PENDING: {
                    TaskStatus.IN_PROGRESS,
                    TaskStatus.CANCELLED,
                },
                TaskStatus.IN_PROGRESS: {
                    TaskStatus.COMPLETED,
                    TaskStatus.CANCELLED,
                },
                TaskStatus.COMPLETED: set(),
                TaskStatus.CANCELLED: set(),
            }

            if (
                new_status != current_status
                and new_status
                not in allowed_transitions[current_status]
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"Cannot change task status from "
                        f"'{current_status.value}' "
                        f"to '{new_status.value}'."
                    ),
                )

            user_task.status = new_status

            if new_status == TaskStatus.COMPLETED:
                user_task.completed_at = datetime.now(
                    timezone.utc,
                )
            else:
                user_task.completed_at = None

        for key, value in update_data.items():
            setattr(
                user_task,
                key,
                value,
            )

        user_task = self.user_task_repository.update_user_task(
            user_task,
        )

        self.invalidate_task_assignment_cache(
            task_id=task_id,
            user_id=user_id,
        )

        logger.info(
            "Updated assignment successfully",
        )

        return user_task
    
    def delete_user_task(
        self,
        task_id: UUID,
        user_id: UUID,
        current_user: User,
    ) -> None:

        logger.info(
            "Removing user %s from task %s",
            user_id,
            task_id,
        )

        assignment = self.user_task_repository.get_user_task(
            user_id=user_id,
            task_id=task_id,
        )

        if assignment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task assignment not found",
            )

        can_access_user_task(
            current_user,
            assignment,
        )

        self.user_task_repository.delete_user_task(
            assignment,
        )

        self.invalidate_task_assignment_cache(
            task_id=task_id,
            user_id=user_id,
        )

        logger.info(
            "Task assignment removed successfully",
        )
        
        
    def invalidate_task_assignment_cache(
        self,
        task_id: UUID,
        user_id: UUID,
    ) -> None:

        self.cache_repository.delete(
            f"taskflow:cache:task_assignment:{task_id}:{user_id}",
        )

        self.cache_repository.delete_pattern(
            f"taskflow:cache:task_assignees:{task_id}*",
        )

        self.cache_repository.delete_pattern(
            "taskflow:cache:user_tasks*",
        )

