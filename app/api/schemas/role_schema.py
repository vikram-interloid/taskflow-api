from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RoleBase(BaseModel):
    name: str = Field(
        validation_alias="role_name",
        serialization_alias="name",
        min_length=3,
        max_length=50,
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
    )


class RoleCreate(RoleBase):
    pass


class RoleResponse(RoleBase):
    role_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class RoleUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        validation_alias="role_name",
        serialization_alias="name",
        min_length=3,
        max_length=50,
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )
