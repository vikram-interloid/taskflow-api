from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, UUID, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.api.database.db_config import Base


class UserTask(Base):
    __tablename__ = 'user_tasks'
    
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "task_id",
            name="uq_user_task",
        ),
    )
    
    id : Mapped[uuid.UUID] = mapped_column (
        UUID(as_uuid = True),
        primary_key = True,
        default=uuid.uuid4
    )
    
    task_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey("tasks.task_id",ondelete="CASCADE"),
        nullable = False,
        index = True
    )
    
    user_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey("users.user_id"),
        nullable = False,
        index = True
    )
    
    created_at : Mapped[datetime] = mapped_column (
        TIMESTAMP(timezone = True),
        server_default = func.now(),
        nullable=False,
    )
    
    due_at : Mapped[datetime] = mapped_column (
        TIMESTAMP(timezone = True),
        nullable=False,
    )
    
    status : Mapped[str] = mapped_column (
        String(25),
        nullable = False
    )
    
    completed_at : Mapped[datetime | None] = mapped_column (
        TIMESTAMP(timezone = True),
        nullable=True,
    )
    
    created_by : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey("users.user_id"),
        nullable = False,
        index = True
    )
    
    
    users : Mapped["User"] = relationship(
        'User',
        foreign_keys=[user_id],
        back_populates = 'user_tasks'
    )
    
    task : Mapped["Task"] = relationship(
        'Task',
        back_populates = 'user_tasks'
    )
    
    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
    )