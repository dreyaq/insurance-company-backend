import uuid
from datetime import date
from typing import List, Optional
from uuid import UUID

from insurance_app.application.interfaces.client_repository import ClientRepository
from insurance_app.application.interfaces.client_service import ClientService
from insurance_app.domain.models.client import Client


class ClientServiceImpl(ClientService):
    """Реализация сервиса для работы с клиентами"""
    
    def __init__(self, client_repository: ClientRepository):
        self.client_repository = client_repository
    
    def create(self, entity: Client) -> Client:
        """Создает нового клиента"""
        # Генерируем ID если его нет
        if entity.id is None:
            entity.id = uuid.uuid4()
        
        # Устанавливаем дату создания
        if entity.created_at is None:
            entity.created_at = date.today()
        
        return self.client_repository.create(entity)
    
    def get_by_id(self, entity_id: UUID) -> Optional[Client]:
        """Получает клиента по идентификатору"""
        return self.client_repository.get_by_id(entity_id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Client]:
        """Получает список клиентов с пагинацией"""
        return self.client_repository.get_all(skip, limit)
    
    def update(self, entity: Client) -> Client:
        """Обновляет существующего клиента"""
        return self.client_repository.update(entity)
    
    def delete(self, entity_id: UUID) -> bool:
        """Удаляет клиента по идентификатору"""
        return self.client_repository.delete(entity_id)
    
    def get_by_email(self, email: str) -> Optional[Client]:
        """Получает клиента по адресу электронной почты"""
        return self.client_repository.get_by_email(email)
    
    def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Client]:
        """Поиск клиентов по имени или фамилии"""
        return self.client_repository.search_by_name(name, skip, limit)
