from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from insurance_app.application.interfaces.claim_repository import ClaimRepository
from insurance_app.domain.models.claim import Claim
from insurance_app.infrastructure.database.models.claim import ClaimModel


class ClaimRepositoryImpl(ClaimRepository):
    """Реализация репозитория для работы с страховыми случаями"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def _to_domain(self, model: ClaimModel) -> Claim:
        """Преобразует ORM модель в доменную модель"""
        return Claim(
            id=model.id,
            claim_number=model.claim_number,
            policy_id=model.policy_id,
            client_id=model.client_id,
            incident_date=model.incident_date,
            report_date=model.report_date,
            description=model.description,
            status=model.status,
            claim_amount=model.claim_amount,
            approved_amount=model.approved_amount,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_active=model.is_active
        )
    
    def _to_model(self, entity: Claim) -> ClaimModel:
        """Преобразует доменную модель в ORM модель"""
        return ClaimModel(
            id=entity.id,
            claim_number=entity.claim_number,
            policy_id=entity.policy_id,
            client_id=entity.client_id,
            incident_date=entity.incident_date,
            report_date=entity.report_date,
            description=entity.description,
            status=entity.status,
            claim_amount=entity.claim_amount,
            approved_amount=entity.approved_amount,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_active=entity.is_active
        )
    
    def create(self, entity: Claim) -> Claim:
        model = self._to_model(entity)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)
    
    def get_by_id(self, entity_id: UUID) -> Optional[Claim]:
        model = self.session.query(ClaimModel).filter(ClaimModel.id == entity_id).first()
        return self._to_domain(model) if model else None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Claim]:
        models = self.session.query(ClaimModel).offset(skip).limit(limit).all()
        return [self._to_domain(model) for model in models]
    
    def update(self, entity: Claim) -> Claim:
        model = self._to_model(entity)
        self.session.merge(model)
        self.session.commit()
        return entity
    
    def delete(self, entity_id: UUID) -> bool:
        model = self.session.query(ClaimModel).filter(ClaimModel.id == entity_id).first()
        if not model:
            return False
        self.session.delete(model)
        self.session.commit()
        return True
    
    def get_by_claim_number(self, claim_number: str) -> Optional[Claim]:
        model = self.session.query(ClaimModel).filter(ClaimModel.claim_number == claim_number).first()
        return self._to_domain(model) if model else None
    
    def get_by_policy_id(self, policy_id: UUID, skip: int = 0, limit: int = 100) -> List[Claim]:
        models = self.session.query(ClaimModel).filter(
            ClaimModel.policy_id == policy_id
        ).offset(skip).limit(limit).all()
        return [self._to_domain(model) for model in models]
    
    def get_by_client_id(self, client_id: UUID, skip: int = 0, limit: int = 100) -> List[Claim]:
        models = self.session.query(ClaimModel).filter(
            ClaimModel.client_id == client_id
        ).offset(skip).limit(limit).all()
        return [self._to_domain(model) for model in models]
