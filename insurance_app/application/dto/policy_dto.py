from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from insurance_app.domain.models.policy import PolicyType, PolicyStatus


class PolicyBaseDTO(BaseModel):
    """Базовая DTO для полиса"""
    policy_number: Optional[str] = Field(None, description="Номер полиса")
    client_id: UUID = Field(..., description="Идентификатор клиента")
    type: PolicyType = Field(..., description="Тип полиса")
    start_date: Optional[date] = Field(None, description="Дата начала действия полиса")
    end_date: Optional[date] = Field(None, description="Дата окончания действия полиса")
    coverage_amount: Decimal = Field(..., description="Страховая сумма", gt=0)
    payment_frequency: str = Field("monthly", description="Частота платежей")
    description: Optional[str] = Field(None, description="Описание полиса")


class PolicyCreateDTO(PolicyBaseDTO):
    """DTO для создания полиса"""
    status: PolicyStatus = Field(default=PolicyStatus.PENDING, description="Статус полиса")
    premium_amount: Optional[Decimal] = Field(None, description="Сумма страховой премии")


class PolicyUpdateDTO(BaseModel):
    """DTO для обновления полиса"""
    policy_number: Optional[str] = Field(None, description="Номер полиса")
    client_id: Optional[UUID] = Field(None, description="Идентификатор клиента")
    type: Optional[PolicyType] = Field(None, description="Тип полиса")
    status: Optional[PolicyStatus] = Field(None, description="Статус полиса")
    start_date: Optional[date] = Field(None, description="Дата начала действия полиса")
    end_date: Optional[date] = Field(None, description="Дата окончания действия полиса")
    coverage_amount: Optional[Decimal] = Field(None, description="Страховая сумма", gt=0)
    premium_amount: Optional[Decimal] = Field(None, description="Сумма страховой премии")
    payment_frequency: Optional[str] = Field(None, description="Частота платежей")
    description: Optional[str] = Field(None, description="Описание полиса")
    is_active: Optional[bool] = Field(None, description="Статус активности полиса")


class PolicyResponseDTO(PolicyBaseDTO):
    """DTO для ответа с данными полиса"""
    id: UUID = Field(..., description="Идентификатор полиса")
    status: PolicyStatus = Field(..., description="Статус полиса")
    premium_amount: Decimal = Field(..., description="Сумма страховой премии")
    created_at: date = Field(..., description="Дата создания полиса")
    is_active: bool = Field(..., description="Статус активности полиса")

    class Config:
        orm_mode = True
