from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, UUID, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.api.database.db_config import Base


class UserRole(Base):
    __tablename__ = 'user_roles'
    
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "role_id",
            name="uq_user_role",
        ),
    )
    
    id: Mapped[uuid.UUID] = mapped_column (
        UUID(as_uuid = True),
        primary_key = True,
        default=uuid.uuid4
    )
    
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey("roles.role_id"),
        nullable = False,
        index = True
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey("users.user_id",ondelete="CASCADE"),
        nullable = False,
        index = True
    )
    
    created_at: Mapped[datetime] = mapped_column (
        TIMESTAMP(timezone = True),
        server_default = func.now(),
        nullable=False,
    )
    
    assigned_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey("users.user_id"),
        nullable = False,
        index = True
    )
    
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="user_roles",
    )

    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="user_roles",
    )

    assigned_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[assigned_by],
        back_populates="assigned_roles",
    )
    
    