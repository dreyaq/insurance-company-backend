import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Date, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from insurance_app.domain.models.claim import ClaimStatus
from insurance_app.infrastructure.database.config import Base


class ClaimModel(Base):
    """ORM модель для таблицы claims"""
    __tablename__ = "claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_number = Column(String, unique=True, nullable=False)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.id"), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    incident_date = Column(Date, nullable=True)
    report_date = Column(Date, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(ClaimStatus), nullable=False, default=ClaimStatus.PENDING)
    claim_amount = Column(Numeric(10, 2), nullable=False)
    approved_amount = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Отношения
    policy = relationship("PolicyModel", backref="claims")
    client = relationship("ClientModel", backref="claims")

    def __repr__(self):
        return f"<Claim {self.claim_number}>"