from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID


class ClaimStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    DENIED = "denied"
    PAID = "paid"
    CLOSED = "closed"


@dataclass
class Claim:
    id: Optional[UUID] = None
    claim_number: str = ""
    policy_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    incident_date: Optional[date] = None
    report_date: Optional[date] = None
    description: str = ""
    status: ClaimStatus = ClaimStatus.PENDING
    claim_amount: Decimal = Decimal("0.00")
    approved_amount: Optional[Decimal] = None
    created_at: Optional[date] = None
    updated_at: Optional[date] = None
    is_active: bool = True