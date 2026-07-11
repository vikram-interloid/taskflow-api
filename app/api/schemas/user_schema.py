from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    user_name: str = Field(
        min_length = 3,
        max_length = 50,
    )
    email: EmailStr
    
    model_config = ConfigDict(extra = 'forbid')

class UserCreate(UserBase):
    password_hash : str = Field(
        min_length = 8,
        max_length = 128
    )

class UserResponse(UserBase):
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    user_name: str | None = Field(
        default = None,
        min_length = 3,
        max_length = 50,
    )
    email: EmailStr | None = None

    model_config = ConfigDict(extra = 'forbid')
    
    
    