from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.models.users_model import User
from app.api.repositories.base_repository import BaseRepository
from app.api.schemas.query_schema import UserQueryParams


class UserRepository(BaseRepository):

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_id(self, user_id: UUID) -> User | None:
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
    ) -> tuple[list[User], int]:

        db_query = self.db.query(User)

        if query.email:
            db_query = db_query.filter(User.email.ilike(f"%{query.email}%"))

        if query.search:
            db_query = db_query.filter(User.user_name.ilike(f"%{query.search}%"))

        total = db_query.count()

        sort_column = getattr(
            User,
            query.sort_by,
            User.created_at,
        )

        if query.order.lower() == "desc":
            db_query = db_query.order_by(sort_column.desc())
        else:
            db_query = db_query.order_by(sort_column.asc())

        users = db_query.offset((query.page - 1) * query.limit).limit(query.limit).all()

        return users, total

    def update_user(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
