from abc import abstractmethod
from typing import Optional, List
from uuid import UUID

from insurance_app.application.interfaces.base_repository import BaseRepository
from insurance_app.domain.models.policy import Policy


class PolicyRepository(BaseRepository[Policy]):
    """Интерфейс репозитория для работы с полисами"""
    
    @abstractmethod
    def get_by_policy_number(self, policy_number: str) -> Optional[Policy]:
        """Получает полис по номеру"""
        pass
    
    @abstractmethod
    def get_by_client_id(self, client_id: UUID, skip: int = 0, limit: int = 100) -> List[Policy]:
        """Получает список полисов клиента"""
        pass
    
    @abstractmethod
    def get_active_policies(self, skip: int = 0, limit: int = 100) -> List[Policy]:
        """Получает список активных полисов"""
        pass