from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, UUID, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.api.database.db_config import Base


class User(Base):
    __tablename__ = 'users'
    
    user_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        primary_key = True,
        default=uuid.uuid4
    )
    
    user_name : Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable = False
    )
    
    email : Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable = False
    )
     
    password_hash : Mapped[str] = mapped_column(
        String(255),
        nullable = False
    )
    
    created_at : Mapped[datetime] = mapped_column (
        TIMESTAMP( timezone = True),
        server_default = func.now(),
        nullable=False,
    )
    
    
    user_tasks: Mapped[list["UserTask"]] = relationship(
        back_populates="user",
    )

    user_roles: Mapped[list["UserRole"]] = relationship(
        back_populates="user",
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user",
    )

    created_tasks: Mapped[list["Task"]] = relationship(
        back_populates="creator",
    )