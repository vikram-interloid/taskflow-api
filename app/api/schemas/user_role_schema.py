from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

class UserRoleBase(BaseModel):
    user_id: UUID
    role_id: UUID

    model_config = ConfigDict(extra="forbid",)


class UserRoleCreate(UserRoleBase):
    pass


class UserRoleUpdate(BaseModel):

    role_id: UUID

    model_config = ConfigDict(extra="forbid")


class UserRoleResponse(UserRoleBase):
    id: UUID
    assigned_by: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

    