from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, BaseModel

class UserTaskBase(BaseModel):
    task_id: UUID
    user_id: UUID
    due_at: datetime
    
    model_config = ConfigDict(extra = "forbid")
    
class UserTaskCreate(UserTaskBase):
    pass

class UserTaskResponse(UserTaskBase):
    id: UUID
    created_at: datetime
    due_at: datetime
    status: str
    completed_at: datetime | None
    created_by: UUID
    
    model_config = ConfigDict(from_attributes = True)
    
class UserTaskUpdate(BaseModel):
    due_at: datetime | None = None
    status: str | None = None
    completed_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")