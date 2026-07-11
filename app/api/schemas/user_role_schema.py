from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserRoleBase(BaseModel):
    user_id: UUID
    role_id: UUID

    model_config = ConfigDict(extra="forbid")

class UserRoleCreate(UserRoleBase):
    assigned_by: UUID

class UserRoleResponse(UserRoleBase):
    id: UUID
    assigned_by: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserRoleUpdate(BaseModel):
    role_id: UUID | None = None

    model_config = ConfigDict(extra="forbid")
    
    