from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from insurance_app.domain.models.claim import ClaimStatus


class ClaimBaseDTO(BaseModel):
    """Базовая DTO для страхового случая"""
    claim_number: Optional[str] = Field(None, description="Номер страхового случая")
    policy_id: UUID = Field(..., description="Идентификатор полиса")
    client_id: Optional[UUID] = Field(None, description="Идентификатор клиента")
    incident_date: Optional[date] = Field(None, description="Дата происшествия")
    description: str = Field(..., description="Описание страхового случая")
    claim_amount: Decimal = Field(..., description="Требуемая сумма выплаты", gt=0)


class ClaimCreateDTO(ClaimBaseDTO):
    """DTO для создания страхового случая"""
    status: ClaimStatus = Field(default=ClaimStatus.PENDING, description="Статус страхового случая")
    report_date: Optional[date] = Field(None, description="Дата подачи заявления")


class ClaimUpdateDTO(BaseModel):
    """DTO для обновления страхового случая"""
    policy_id: Optional[UUID] = Field(None, description="Идентификатор полиса")
    client_id: Optional[UUID] = Field(None, description="Идентификатор клиента")
    incident_date: Optional[date] = Field(None, description="Дата происшествия")
    description: Optional[str] = Field(None, description="Описание страхового случая")
    status: Optional[ClaimStatus] = Field(None, description="Статус страхового случая")
    claim_amount: Optional[Decimal] = Field(None, description="Требуемая сумма выплаты", gt=0)
    approved_amount: Optional[Decimal] = Field(None, description="Утвержденная сумма выплаты")
    is_active: Optional[bool] = Field(None, description="Статус активности страхового случая")


class ClaimResponseDTO(ClaimBaseDTO):
    """DTO для ответа с данными страхового случая"""
    id: UUID = Field(..., description="Идентификатор страхового случая")
    status: ClaimStatus = Field(..., description="Статус страхового случая")
    report_date: date = Field(..., description="Дата подачи заявления")
    approved_amount: Optional[Decimal] = Field(None, description="Утвержденная сумма выплаты")
    created_at: date = Field(..., description="Дата создания страхового случая")
    updated_at: date = Field(..., description="Дата обновления страхового случая")
    is_active: bool = Field(..., description="Статус активности страхового случая")

    class Config:
        orm_mode = True
        
        
class ClaimApproveDTO(BaseModel):
    """DTO для утверждения страхового случая"""
    approved_amount: Decimal = Field(..., description="Утвержденная сумма выплаты", gt=0)
