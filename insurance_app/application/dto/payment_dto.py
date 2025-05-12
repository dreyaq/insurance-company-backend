from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from insurance_app.domain.models.payment import PaymentStatus, PaymentType


class PaymentBaseDTO(BaseModel):
    """Базовая DTO для платежа"""
    payment_number: Optional[str] = Field(None, description="Номер платежа")
    client_id: Optional[UUID] = Field(None, description="Идентификатор клиента")
    policy_id: Optional[UUID] = Field(None, description="Идентификатор полиса")
    claim_id: Optional[UUID] = Field(None, description="Идентификатор страхового случая")
    amount: Decimal = Field(..., description="Сумма платежа", gt=0)
    payment_type: PaymentType = Field(..., description="Тип платежа")
    payment_method: Optional[str] = Field(None, description="Способ оплаты")
    description: Optional[str] = Field(None, description="Описание платежа")


class PaymentCreateDTO(PaymentBaseDTO):
    """DTO для создания платежа"""
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Статус платежа")
    due_date: Optional[date] = Field(None, description="Срок оплаты")
    payment_date: Optional[date] = Field(None, description="Дата платежа")


class PaymentUpdateDTO(BaseModel):
    """DTO для обновления платежа"""
    client_id: Optional[UUID] = Field(None, description="Идентификатор клиента")
    policy_id: Optional[UUID] = Field(None, description="Идентификатор полиса")
    claim_id: Optional[UUID] = Field(None, description="Идентификатор страхового случая")
    status: Optional[PaymentStatus] = Field(None, description="Статус платежа")
    amount: Optional[Decimal] = Field(None, description="Сумма платежа", gt=0)
    payment_date: Optional[date] = Field(None, description="Дата платежа")
    due_date: Optional[date] = Field(None, description="Срок оплаты")
    payment_method: Optional[str] = Field(None, description="Способ оплаты")
    payment_type: Optional[PaymentType] = Field(None, description="Тип платежа")
    description: Optional[str] = Field(None, description="Описание платежа")
    is_active: Optional[bool] = Field(None, description="Статус активности платежа")


class PaymentResponseDTO(PaymentBaseDTO):
    """DTO для ответа с данными платежа"""
    id: UUID = Field(..., description="Идентификатор платежа")
    status: PaymentStatus = Field(..., description="Статус платежа")
    payment_date: Optional[date] = Field(None, description="Дата платежа")
    due_date: Optional[date] = Field(None, description="Срок оплаты")
    created_at: date = Field(..., description="Дата создания платежа")
    is_active: bool = Field(..., description="Статус активности платежа")

    class Config:
        orm_mode = True


class PaymentProcessDTO(BaseModel):
    """DTO для обработки платежа"""
    payment_date: Optional[date] = Field(None, description="Дата платежа")
