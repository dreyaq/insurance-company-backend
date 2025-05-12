import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Date, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from insurance_app.domain.models.policy import PolicyStatus, PolicyType
from insurance_app.infrastructure.database.config import Base


class PolicyModel(Base):
    """ORM модель для таблицы policies"""
    __tablename__ = "policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_number = Column(String, unique=True, nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    type = Column(Enum(PolicyType), nullable=False)
    status = Column(Enum(PolicyStatus), nullable=False, default=PolicyStatus.PENDING)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    coverage_amount = Column(Numeric(10, 2), nullable=False)
    premium_amount = Column(Numeric(10, 2), nullable=False)
    payment_frequency = Column(String, nullable=False, default="monthly")
    created_at = Column(DateTime, default=datetime.utcnow)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    # Отношения
    client = relationship("ClientModel", backref="policies")

    def __repr__(self):
        return f"<Policy {self.policy_number}>"