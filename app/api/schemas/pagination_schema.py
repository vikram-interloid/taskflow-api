from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)

    model_config = ConfigDict(extra="forbid")


class PaginatedResponse(GenericModel, Generic[T]):
    page: int
    limit: int
    total: int
    data: list[T]
