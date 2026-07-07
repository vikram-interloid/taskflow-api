from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, UUID, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.api.database.db_config import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        primary_key = True,
        default=uuid.uuid4
    )
    
    token_hash: Mapped[str] = mapped_column (
        String(255),
        unique = True,
        nullable = False
    )
    
    expires_at: Mapped[datetime] = mapped_column (
        TIMESTAMP( timezone = True),
        nullable=False,
    )
    
    created_at: Mapped[datetime] = mapped_column (
        TIMESTAMP( timezone = True),
        server_default = func.now(),
        nullable=False,
    )
    
    updated_at: Mapped[datetime] = mapped_column (
        TIMESTAMP( timezone = True),
        server_default = func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column (
        UUID(as_uuid = True),
        ForeignKey("users.user_id",ondelete="CASCADE"),
        nullable = False,
        index = True
    )
    
    users: Mapped[User] = relationship (
        "User",
        back_populates = "refresh_tokens"
    )