from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(
        validation_alias="user_name",
        serialization_alias="name",
        min_length=3,
        max_length=50,
    )

    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
    )


class UserCreate(UserBase):
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(UserBase):
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class UserUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        validation_alias="user_name",
        serialization_alias="name",
        min_length=3,
        max_length=50,
    )

    email: EmailStr | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )
