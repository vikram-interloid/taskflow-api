from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.models.users_model import User
from app.api.repositories.base_repository import BaseRepository
from app.api.schemas.query_schema import UserQueryParams


class UserRepository(BaseRepository):
    
    def __init__(self,db: Session):
        self.db = db
    
    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_id(self,user_id: UUID) -> User | None:
        stmt = select(User).where(User.user_id == user_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_user_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.user_name == username)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_all_users(
        self,
        query: UserQueryParams,
    ):

        stmt = select(User)

        filters = {
            "email": User.email,
        }

        stmt = self.apply_filters(
            stmt=stmt,
            filters=filters,
            query=query,
        )

        stmt = self.apply_search(
            stmt=stmt,
            search=query.search,
            columns=[
                User.user_name,
                User.email,
            ],
        )

        sortable_columns = {
            "user_name": User.user_name,
            "email": User.email,
            "created_at": User.created_at,
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
    
    
    def update_user(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user
        
    
    def delete_user(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()

        
