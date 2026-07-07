from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, UUID, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.api.database.db_config import Base


class Role(Base):
    __tablename__ = "roles"
    
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        primary_key = True,
        default=uuid.uuid4
    )
    
    role_name: Mapped[str] = mapped_column (
        String(50),
        unique=True,
        nullable = False
    )
    
    created_at: Mapped[datetime] = mapped_column (
        TIMESTAMP( timezone = True),
        server_default = func.now()
    )
    
    user_roles: Mapped[list["UserRole"]] = relationship(
        back_populates = 'role'
    )

