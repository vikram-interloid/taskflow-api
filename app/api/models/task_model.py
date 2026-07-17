from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, UUID, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.api.database.db_config import Base


class Task(Base):
    __tablename__ = "tasks"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        "task_name",
        String(50),
        nullable=False,
    )

    desc: Mapped[str] = mapped_column(
        "task_desc",
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True
    )

    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_tasks",
        foreign_keys=[created_by],
    )

    user_tasks: Mapped[list["UserTask"]] = relationship(
        "UserTask", back_populates="task"
    )
