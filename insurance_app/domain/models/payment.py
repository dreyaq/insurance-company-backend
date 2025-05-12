from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentType(str, Enum):
    PREMIUM = "premium"
    CLAIM_PAYOUT = "claim_payout"
    REFUND = "refund"


@dataclass
class Payment:
    id: Optional[UUID] = None
    payment_number: str = ""
    client_id: Optional[UUID] = None
    policy_id: Optional[UUID] = None
    claim_id: Optional[UUID] = None
    amount: Decimal = Decimal("0.00")
    payment_date: Optional[date] = None
    due_date: Optional[date] = None
    status: PaymentStatus = PaymentStatus.PENDING
    payment_type: PaymentType = PaymentType.PREMIUM
    payment_method: str = ""
    description: str = ""
    created_at: Optional[date] = None
    is_active: bool = True