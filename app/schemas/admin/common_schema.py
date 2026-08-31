from pydantic import BaseModel
from typing import Any


class MessageResponse(BaseModel):

    success: bool = True
    message: str





class ApiResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: Any = None