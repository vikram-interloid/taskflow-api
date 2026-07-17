from typing import Any

from pydantic import BaseModel, ConfigDict

class ErrorBase(BaseModel):
    code: str
    message: str
    detail: Any | None = None
    
    model_config = ConfigDict(from_attributes = True)
    