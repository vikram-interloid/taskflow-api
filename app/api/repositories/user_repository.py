from uuid  import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.models.users_model import User


class UserRepository:
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
    
    def get_all_users(self):
        stmt = select(User)
        result = self.db.execute(stmt)
        return result.scalars().all()
    
    def update_user(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user
        
    
    def delete_user(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()

        
