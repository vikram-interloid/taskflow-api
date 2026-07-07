from datetime import datetime
from uuid import UUID

from pydantic import Field, ConfigDict, BaseModel

class RoleBase(BaseModel):
    role_name: str
    
    model_config = ConfigDict(extra = 'forbid')
    
class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    role_id: UUID
    created_at : datetime
    
    model_config = ConfigDict(from_attributes = True)
    
class RoleUpdate(BaseModel):
    role_name: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
    )

    model_config = ConfigDict(extra="forbid")