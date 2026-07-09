from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.models.roles_model import Role
from app.api.models.user_role import UserRole
from app.api.repositories.base_repository import BaseRepository
from app.api.schemas.query_schema import UserRoleQueryParams

class UserRoleRepository(BaseRepository):
	def __init__(self,db: Session):
		self.db = db

	def create_user_role(
			self,
			user_role: UserRole
	) -> UserRole:
			self.db.add(user_role)
			self.db.commit()
			self.db.refresh(user_role)
			return user_role

	def get_user_role_by_id(
		self,
		user_role_id: UUID
	) -> UserRole | None:
			stmt = select(UserRole).where(UserRole.id == user_role_id)
			result = self.db.execute(stmt)
			return result.scalar_one_or_none()

	def get_user_role(
			self,
			user_id: UUID,
			role_id: UUID,
	) -> UserRole | None:
			stmt = select(UserRole).where(
						UserRole.user_id == user_id ,
						UserRole.role_id == role_id  )
			result = self.db.execute(stmt)
			return result.scalar_one_or_none()


	def get_all_user_roles(
		self,
		query: UserRoleQueryParams,
	):

		stmt = select(UserRole)

		filters = {
			"user_id": UserRole.user_id,
			"role_id": UserRole.role_id,
			"assigned_by": UserRole.assigned_by,
		}

		stmt = self.apply_filters(
			stmt=stmt,
			filters=filters,
			query=query,
		)

		stmt = self.apply_sort(
			stmt=stmt,
			sortable_columns={
				"assigned_at": UserRole.assigned_at,
			},
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


	def update_user_role(
			self,
			user_role: UserRole
	) -> UserRole:
			self.db.commit()
			self.db.refresh(user_role)
			return user_role

	def delete_user_role(
			self,
			user_role: UserRole
	) -> None:
			self.db.delete(user_role)
			self.db.commit()
   

	def get_roles_by_user_id(self, user_id: UUID):
		stmt = (
			select(Role)
			.join(UserRole, Role.role_id == UserRole.role_id)
			.where(UserRole.user_id == user_id)
		)
		result = self.db.execute(stmt)
		return result.scalars().all()
