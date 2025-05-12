from abc import abstractmethod
from typing import Optional, List
from uuid import UUID

from insurance_app.application.interfaces.base_service import BaseService
from insurance_app.domain.models.client import Client


class ClientService(BaseService[Client]):
    """Интерфейс сервиса для работы с клиентами"""
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Client]:
        """Получает клиента по адресу электронной почты"""
        pass
    
    @abstractmethod
    def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Client]:
        """Поиск клиентов по имени или фамилии"""
        pass
