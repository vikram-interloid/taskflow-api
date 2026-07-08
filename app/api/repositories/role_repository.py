from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.models.roles_model import Role

class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_role(self, role: Role) -> Role:
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def get_role_by_id(self, role_id: UUID) -> Role | None:
        stmt = select(Role).where(Role.role_id == role_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_role_by_name(self, role_name: str) -> Role | None:
        stmt = select(Role).where(Role.role_name == role_name)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_all_roles(self):
        stmt = select(Role)
        result = self.db.execute(stmt)
        return result.scalars().all()

    
    def update_role(self, role: Role) -> Role:
        self.db.commit()
        self.db.refresh(role)
        return role


    def delete_role(self, role: Role) -> None:
        self.db.delete(role)
        self.db.commit()
        