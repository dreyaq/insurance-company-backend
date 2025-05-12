from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from insurance_app.application.interfaces.payment_repository import PaymentRepository
from insurance_app.domain.models.payment import Payment
from insurance_app.infrastructure.database.models.payment import PaymentModel


class PaymentRepositoryImpl(PaymentRepository):
    """Реализация репозитория для работы с платежами"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def _to_domain(self, model: PaymentModel) -> Payment:
        """Преобразует ORM модель в доменную модель"""
        return Payment(
            id=model.id,
            payment_number=model.payment_number,
            client_id=model.client_id,
            policy_id=model.policy_id,
            claim_id=model.claim_id,
            amount=model.amount,
            payment_date=model.payment_date,
            due_date=model.due_date,
            status=model.status,
            payment_type=model.payment_type,
            payment_method=model.payment_method,
            description=model.description,
            created_at=model.created_at,
            is_active=model.is_active
        )
    
    def _to_model(self, entity: Payment) -> PaymentModel:
        """Преобразует доменную модель в ORM модель"""
        return PaymentModel(
            id=entity.id,
            payment_number=entity.payment_number,
            client_id=entity.client_id,
            policy_id=entity.policy_id,
            claim_id=entity.claim_id,
            amount=entity.amount,
            payment_date=entity.payment_date,
            due_date=entity.due_date,
            status=entity.status,
            payment_type=entity.payment_type,
            payment_method=entity.payment_method,
            description=entity.description,
            created_at=entity.created_at,
            is_active=entity.is_active
        )
    
    def create(self, entity: Payment) -> Payment:
        model = self._to_model(entity)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)
    
    def get_by_id(self, entity_id: UUID) -> Optional[Payment]:
        model = self.session.query(PaymentModel).filter(PaymentModel.id == entity_id).first()
        return self._to_domain(model) if model else None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Payment]:
        models = self.session.query(PaymentModel).offset(skip).limit(limit).all()
        return [self._to_domain(model) for model in models]
    
    def update(self, entity: Payment) -> Payment:
        model = self._to_model(entity)
        self.session.merge(model)
        self.session.commit()
        return entity
    
    def delete(self, entity_id: UUID) -> bool:
        model = self.session.query(PaymentModel).filter(PaymentModel.id == entity_id).first()
        if not model:
            return False
        self.session.delete(model)
        self.session.commit()
        return True
    
    def get_by_payment_number(self, payment_number: str) -> Optional[Payment]:
        model = self.session.query(PaymentModel).filter(PaymentModel.payment_number == payment_number).first()
        return self._to_domain(model) if model else None
    
    def get_by_client_id(self, client_id: UUID, skip: int = 0, limit: int = 100) -> List[Payment]:
        models = self.session.query(PaymentModel).filter(
            PaymentModel.client_id == client_id
        ).offset(skip).limit(limit).all()
        return [self._to_domain(model) for model in models]
    
    def get_by_policy_id(self, policy_id: UUID, skip: int = 0, limit: int = 100) -> List[Payment]:
        models = self.session.query(PaymentModel).filter(
            PaymentModel.policy_id == policy_id
        ).offset(skip).limit(limit).all()
        return [self._to_domain(model) for model in models]
    
    def get_by_claim_id(self, claim_id: UUID, skip: int = 0, limit: int = 100) -> List[Payment]:
        models = self.session.query(PaymentModel).filter(
            PaymentModel.claim_id == claim_id
        ).offset(skip).limit(limit).all()
        return [self._to_domain(model) for model in models]
