from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from insurance_app.application.interfaces.client_repository import ClientRepository
from insurance_app.domain.models.client import Client
from insurance_app.infrastructure.database.models.client import ClientModel


class ClientRepositoryImpl(ClientRepository):
    """Реализация репозитория для работы с клиентами"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def _to_domain(self, model: ClientModel) -> Client:
        return Client(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            phone=model.phone,
            birth_date=model.birth_date,
            address=model.address,
            passport_number=model.passport_number,
            created_at=model.created_at,
            is_active=model.is_active
        )
    
    def _to_model(self, entity: Client) -> ClientModel:
        return ClientModel(
            id=entity.id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            email=entity.email,
            phone=entity.phone,
            birth_date=entity.birth_date,
            address=entity.address,
            passport_number=entity.passport_number,
            created_at=entity.created_at,
            is_active=entity.is_active
        )
    
    def create(self, entity: Client) -> Client:
        model = self._to_model(entity)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)
    
    def get_by_id(self, entity_id: UUID) -> Optional[Client]:
        model = self.session.query(ClientModel).filter(ClientModel.id == entity_id).first()
        return self._to_domain(model) if model else None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Client]:
        models = self.session.query(ClientModel).offset(skip).limit(limit).all()
        return [self._to_domain(model) for model in models]
    
    def update(self, entity: Client) -> Client:
        model = self._to_model(entity)
        self.session.merge(model)
        self.session.commit()
        return entity
    
    def delete(self, entity_id: UUID) -> bool:
        model = self.session.query(ClientModel).filter(ClientModel.id == entity_id).first()
        if not model:
            return False
        self.session.delete(model)
        self.session.commit()
        return True
    
    def get_by_email(self, email: str) -> Optional[Client]:
        model = self.session.query(ClientModel).filter(ClientModel.email == email).first()
        return self._to_domain(model) if model else None
    
    def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Client]:
        models = self.session.query(ClientModel).filter(
            (ClientModel.first_name.ilike(f"%{name}%")) | 
            (ClientModel.last_name.ilike(f"%{name}%"))
        ).offset(skip).limit(limit).all()
        return [self._to_domain(model) for model in models]