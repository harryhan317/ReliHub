"""
Standardized API response wrappers.
Aligned with: API_错误码对照表.md §1.3.
"""
from typing import Any, Optional

from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: str = "000000"
    msg: str = "success"
    data: Any = {}


class ErrorResponse(BaseModel):
    code: str
    msg: str
    data: Optional[dict] = {}
