from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID


class PolicyStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "canceled"
    PENDING = "pending"


class PolicyType(str, Enum):
    LIFE = "life"
    HEALTH = "health"
    PROPERTY = "property"
    VEHICLE = "vehicle"
    TRAVEL = "travel"


@dataclass
class Policy:
    id: Optional[UUID] = None
    policy_number: str = ""
    client_id: Optional[UUID] = None
    type: PolicyType = PolicyType.HEALTH
    status: PolicyStatus = PolicyStatus.PENDING
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    coverage_amount: Decimal = Decimal("0.00")
    premium_amount: Decimal = Decimal("0.00")
    payment_frequency: str = "monthly"
    created_at: Optional[date] = None
    description: str = ""
    is_active: bool = True