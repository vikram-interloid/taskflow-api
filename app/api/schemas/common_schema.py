from typing import Any

from pydantic import BaseModel, ConfigDict


class MessageResponse(BaseModel):
    message: str

    model_config = ConfigDict(from_attributes=True)


class SuccessResponse(BaseModel):
    success: bool = True
    message: str

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    detail: Any | None = None

    model_config = ConfigDict(from_attributes=True)