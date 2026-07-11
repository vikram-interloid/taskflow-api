from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.core.dependencies import get_current_user
from app.api.enums.roles import RoleName
from app.api.database.db_config import get_db
from app.api.models.users_model import User
from app.api.repositories.user_role_repository import UserRoleRepository


def require_roles(allowed_roles: list[RoleName]):

    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:

        repository = UserRoleRepository(db)

        roles = repository.get_roles_by_user_id(
            current_user.user_id,
        )

        user_roles = {
            role.role_name
            for role in roles
        }

        allowed = {
            role.value
            for role in allowed_roles
        }

        if user_roles.isdisjoint(allowed):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_checker

