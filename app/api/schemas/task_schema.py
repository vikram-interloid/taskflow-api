from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    name: str = Field(
        min_length=5,
        max_length=50,
    )

    desc: str = Field(
        min_length=5,
        max_length=255,
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    task_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class TaskUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=5,
        max_length=50,
    )

    desc: str | None = Field(
        default=None,
        min_length=5,
        max_length=255,
    )

    model_config = ConfigDict(
        extra="forbid",
    )
    