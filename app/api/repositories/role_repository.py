from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.models.roles_model import Role
from app.api.repositories.base_repository import BaseRepository
from app.api.schemas.query_schema import RoleQueryParams


class RoleRepository(BaseRepository):

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

    def get_all_roles(
        self,
        query: RoleQueryParams,
    ):

        stmt = select(Role)

        stmt = self.apply_search(
            stmt=stmt,
            search=query.search,
            columns=[
                Role.role_name,
            ],
        )

        sortable_columns = {
            "role_name": Role.role_name,
            "created_at": Role.created_at,
        }

        stmt = self.apply_sort(
            stmt=stmt,
            sortable_columns=sortable_columns,
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

    def update_role(self, role: Role) -> Role:
        self.db.commit()
        self.db.refresh(role)
        return role

    def delete_role(self, role: Role) -> None:
        self.db.delete(role)
        self.db.commit()
