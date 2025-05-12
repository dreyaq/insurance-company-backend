from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from insurance_app.application.interfaces.policy_repository import PolicyRepository
from insurance_app.domain.models.policy import Policy, PolicyStatus
from insurance_app.infrastructure.database.models.policy import PolicyModel


class PolicyRepositoryImpl(PolicyRepository):
    """Реализация репозитория для работы с полисами"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def _to_domain(self, model: PolicyModel) -> Policy:
        return Policy(
            id=model.id,
            policy_number=model.policy_number,
            client_id=model.client_id,
            type=model.type,
            status=model.status,
            start_date=model.start_date,
            end_date=model.end_date,
            coverage_amount=model.coverage_amount,
            premium_amount=model.premium_amount,
            payment_frequency=model.payment_frequency,
            created_at=model.created_at,
            description=model.description,
            is_active=model.is_active
        )
    
    def _to_model(self, entity: Policy) -> PolicyModel:
        return PolicyModel(
            id=entity.id,
            policy_number=entity.policy_number,
            client_id=entity.client_id,
            type=entity.type,
            status=entity.status,
            start_date=entity.start_date,
            end_date=entity.end_date,
            coverage_amount=entity.coverage_amount,
            premium_amount=entity.premium_amount,
            payment_frequency=entity.payment_frequency,
            created_at=entity.created_at,
            description=entity.description,
            is_active=entity.is_active
        )
    
    def create(self, entity: Policy) -> Policy:
        model = self._to_model(entity)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)
    
    def get_by_id(self, entity_id: UUID) -> Optional[Policy]:
        model = self.session.query(PolicyModel).filter(PolicyModel.id == entity_id).first()
        return self._to_domain(model) if model else None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Policy]:
        models = self.session.query(PolicyModel).offset(skip).limit(limit).all()
        return [self._to_domain(model) for model in models]
    
    def update(self, entity: Policy) -> Policy:
        model = self._to_model(entity)
        self.session.merge(model)
        self.session.commit()
        return entity
    
    def delete(self, entity_id: UUID) -> bool:
        model = self.session.query(PolicyModel).filter(PolicyModel.id == entity_id).first()
        if not model:
            return False
        self.session.delete(model)
        self.session.commit()
        return True
    
    def get_by_policy_number(self, policy_number: str) -> Optional[Policy]:
        model = self.session.query(PolicyModel).filter(PolicyModel.policy_number == policy_number).first()
        return self._to_domain(model) if model else None
    
    def get_by_client_id(self, client_id: UUID, skip: int = 0, limit: int = 100) -> List[Policy]:
        models = self.session.query(PolicyModel).filter(
            PolicyModel.client_id == client_id
        ).offset(skip).limit(limit).all()
        return [self._to_domain(model) for model in models]
    
    def get_active_policies(self, skip: int = 0, limit: int = 100) -> List[Policy]:
        models = self.session.query(PolicyModel).filter(
            (PolicyModel.status == PolicyStatus.ACTIVE) & 
            (PolicyModel.is_active == True)
        ).offset(skip).limit(limit).all()
        return [self._to_domain(model) for model in models]
