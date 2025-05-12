from abc import abstractmethod
from typing import Optional, List
from uuid import UUID

from insurance_app.application.interfaces.base_repository import BaseRepository
from insurance_app.domain.models.payment import Payment


class PaymentRepository(BaseRepository[Payment]):
    """Интерфейс репозитория для работы с платежами"""
    
    @abstractmethod
    def get_by_payment_number(self, payment_number: str) -> Optional[Payment]:
        """Получает платеж по номеру"""
        pass
    
    @abstractmethod
    def get_by_client_id(self, client_id: UUID, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Получает список платежей клиента"""
        pass
    
    @abstractmethod
    def get_by_policy_id(self, policy_id: UUID, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Получает список платежей по полису"""
        pass
    
    @abstractmethod
    def get_by_claim_id(self, claim_id: UUID, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Получает список платежей по страховому случаю"""
        pass