from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.core.dependencies import get_current_user
from app.api.database.db_config import get_db
from app.api.models.users_model import User
from app.api.repositories.user_role_repository import UserRoleRepository


def require_roles(allowed_roles: list[str]):

    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:

        print("Logged in user:", current_user.user_id)

        repository = UserRoleRepository(db)

        roles = repository.get_roles_by_user_id(current_user.user_id)

        print("Roles from DB:",[r.role_name for r in roles])
        print("Allowed:", allowed_roles)

        user_roles = [r.role_name for r in roles]

        if not any(role in allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_checker