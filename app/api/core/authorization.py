from fastapi import HTTPException, status

from app.api.enums.roles import RoleName
from app.api.models.user_task import UserTask
from app.api.models.users_model import User


def can_access_user_task(
    current_user: User,
    user_task: UserTask,
) -> None:
    
    for user_role in current_user.user_roles:
        role_name = user_role.role.role_name

        if role_name == RoleName.ADMIN:
            return

        if (
            role_name == RoleName.MANAGER
            and user_task.created_by == current_user.user_id
        ):
            return

    if current_user.user_id == user_task.user_id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Permission denied",
    )
    
    