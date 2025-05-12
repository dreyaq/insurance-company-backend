from abc import abstractmethod
from typing import Optional, List
from uuid import UUID
from datetime import date

from insurance_app.application.interfaces.base_service import BaseService
from insurance_app.domain.models.payment import Payment, PaymentStatus


class PaymentService(BaseService[Payment]):
    """Интерфейс сервиса для работы с платежами"""
    
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
    
    @abstractmethod
    def process_payment(self, payment_id: UUID, payment_date: date = None) -> Payment:
        """Обрабатывает платеж, меняя его статус на COMPLETED"""
        pass
    
    @abstractmethod
    def create_premium_payment(self, policy_id: UUID) -> Payment:
        """Создает платеж страховой премии для полиса"""
        pass
    
    @abstractmethod
    def create_claim_payout(self, claim_id: UUID) -> Payment:
        """Создает платеж страховой выплаты по страховому случаю"""
        pass
