from typing import List, Generic, TypeVar, Optional
from pydantic import BaseModel, Field


T = TypeVar('T')


class PaginationDTO(BaseModel):
    """DTO для пагинации"""
    skip: int = Field(0, description="Количество пропускаемых записей", ge=0)
    limit: int = Field(100, description="Количество записей на странице", ge=1, le=1000)


class PaginatedResponseDTO(Generic[T], BaseModel):
    """DTO для ответа с пагинацией"""
    items: List[T] = Field(..., description="Список элементов")
    total: int = Field(..., description="Общее количество элементов")
    skip: int = Field(..., description="Количество пропущенных элементов")
    limit: int = Field(..., description="Количество элементов на странице")


class ErrorDTO(BaseModel):
    """DTO для ошибок"""
    code: str = Field(..., description="Код ошибки")
    message: str = Field(..., description="Сообщение об ошибке")
    details: Optional[str] = Field(None, description="Подробности ошибки")
