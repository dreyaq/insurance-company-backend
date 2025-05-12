import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Date, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from insurance_app.domain.models.payment import PaymentStatus, PaymentType
from insurance_app.infrastructure.database.config import Base


class PaymentModel(Base):
    """ORM модель для таблицы payments"""
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_number = Column(String, unique=True, nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.id"), nullable=True)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    payment_type = Column(Enum(PaymentType), nullable=False)
    payment_method = Column(String, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Отношения
    client = relationship("ClientModel", backref="payments")
    policy = relationship("PolicyModel", backref="payments")
    claim = relationship("ClaimModel", backref="payments")

    def __repr__(self):
        return f"<Payment {self.payment_number}>"