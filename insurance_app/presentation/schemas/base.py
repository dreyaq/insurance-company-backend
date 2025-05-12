from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Схема ответа для проверки состояния API"""
    status: str = Field("ok", description="Статус API")
    version: str = Field(..., description="Версия API")


class ErrorResponse(BaseModel):
    """Базовая схема ответа с ошибкой"""
    error: str = Field(..., description="Код ошибки")
    message: str = Field(..., description="Сообщение об ошибке")
    details: Optional[Union[List[Dict[str, Any]], Dict[str, Any], str]] = Field(
        None, description="Дополнительные детали ошибки"
    )
