from fastapi import HTTPException, status

from app.api.models.user_task import UserTask
from app.api.models.users_model import User


def can_access_user_task(
    current_user: User,
    user_task: UserTask
) -> None:
    
    if any(
        user_role.role.role_name == "Admin"
        for user_role in current_user.user_roles
    ):
        return

    if current_user.user_id != user_task.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task.",
        )
        
