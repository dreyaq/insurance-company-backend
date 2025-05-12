from datetime import date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class ClientBaseDTO(BaseModel):
    """Базовая DTO для клиента"""
    first_name: str = Field(..., description="Имя клиента")
    last_name: str = Field(..., description="Фамилия клиента")
    email: EmailStr = Field(..., description="Email клиента")
    phone: Optional[str] = Field(None, description="Телефон клиента")
    birth_date: Optional[date] = Field(None, description="Дата рождения клиента")
    address: Optional[str] = Field(None, description="Адрес клиента")
    passport_number: Optional[str] = Field(None, description="Номер паспорта клиента")


class ClientCreateDTO(ClientBaseDTO):
    """DTO для создания клиента"""
    pass


class ClientUpdateDTO(BaseModel):
    """DTO для обновления клиента"""
    first_name: Optional[str] = Field(None, description="Имя клиента")
    last_name: Optional[str] = Field(None, description="Фамилия клиента")
    email: Optional[EmailStr] = Field(None, description="Email клиента")
    phone: Optional[str] = Field(None, description="Телефон клиента")
    birth_date: Optional[date] = Field(None, description="Дата рождения клиента")
    address: Optional[str] = Field(None, description="Адрес клиента")
    passport_number: Optional[str] = Field(None, description="Номер паспорта клиента")
    is_active: Optional[bool] = Field(None, description="Статус активности клиента")


class ClientResponseDTO(ClientBaseDTO):
    """DTO для ответа с данными клиента"""
    id: UUID = Field(..., description="Идентификатор клиента")
    created_at: date = Field(..., description="Дата создания клиента")
    is_active: bool = Field(..., description="Статус активности клиента")

    class Config:
        orm_mode = True
