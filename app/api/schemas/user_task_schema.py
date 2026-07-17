from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.api.enums.task_status import TaskStatus


class UserTaskBase(BaseModel):
    user_id: UUID
    due_at: datetime

    model_config = ConfigDict(
        extra="forbid",
    )


class UserTaskCreate(UserTaskBase):
    pass


class UserTaskResponse(BaseModel):
    id: UUID
    task_id: UUID
    user_id: UUID
    due_at: datetime
    status: TaskStatus
    completed_at: datetime | None = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserTaskUpdate(BaseModel):
    due_at: datetime | None = None
    status: TaskStatus | None = None

    model_config = ConfigDict(
        extra="forbid",
    )
