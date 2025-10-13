"""
Базовые схемы для API responses
Согласно TECHNICAL.md все endpoints должны возвращать единый формат
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from datetime import datetime


class APIResponseMeta(BaseModel):
    """Метаданные для API response"""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class APIErrorDetails(BaseModel):
    """Детали ошибки API"""
    field: Optional[str] = None
    reason: Optional[str] = None
    code: Optional[str] = None


class APIError(BaseModel):
    """Структура ошибки API согласно TECHNICAL.md"""
    code: str
    message: str
    details: Optional[APIErrorDetails] = None


class APIResponse(BaseModel):
    """
    Базовый формат ответа API согласно TECHNICAL.md
    Формат: {"data": {...}, "error": null, "meta": {"timestamp": "..."}}
    """
    data: Optional[Any] = None
    error: Optional[APIError] = None
    meta: APIResponseMeta = Field(default_factory=APIResponseMeta)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class APISuccessResponse(APIResponse):
    """Response для успешных операций"""
    error: None = None


class APIErrorResponse(APIResponse):
    """Response для ошибок"""
    data: None = None