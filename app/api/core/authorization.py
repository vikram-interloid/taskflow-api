from uuid import UUID

from fastapi import HTTPException, status

from app.api.enums.roles import RoleName
from app.api.models.roles_model import Role
from app.api.models.task_model import Task
from app.api.models.user_role import UserRole
from app.api.models.user_task import UserTask
from app.api.models.users_model import User


def is_admin(current_user: User) -> bool:
    return any(
        user_role.role.role_name == RoleName.ADMIN
        for user_role in current_user.user_roles
    )


def is_manager(current_user: User) -> bool:
    return any(
        user_role.role.role_name == RoleName.MANAGER
        for user_role in current_user.user_roles
    )


def can_access_role(
    current_user: User,
    role: Role,
) -> None:

    if is_admin(current_user):
        return

    for user_role in current_user.user_roles:
        if user_role.role_id == role.role_id:
            return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Permission denied",
    )


def can_access_user(
    current_user: User,
    target_user_id: UUID,
) -> None:

    if is_admin(current_user):
        return

    if current_user.user_id == target_user_id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Permission denied",
    )


def can_access_task(
    current_user: User,
    task: Task,
) -> None:

    if is_admin(current_user):
        return

    if is_manager(current_user) and task.created_by == current_user.user_id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Permission denied",
    )


def can_access_user_role(
    current_user: User,
    user_role: UserRole,
) -> None:

    if is_admin(current_user):
        return

    if current_user.user_id == user_role.user_id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Permission denied",
    )


def can_access_user_task(
    current_user: User,
    user_task: UserTask,
) -> None:

    if is_admin(current_user):
        return

    if is_manager(current_user) and user_task.created_by == current_user.user_id:
        return

    if current_user.user_id == user_task.user_id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Permission denied",
    )
