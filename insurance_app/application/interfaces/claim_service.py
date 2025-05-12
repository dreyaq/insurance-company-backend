from abc import abstractmethod
from typing import Optional, List
from uuid import UUID

from insurance_app.application.interfaces.base_service import BaseService
from insurance_app.domain.models.claim import Claim, ClaimStatus


class ClaimService(BaseService[Claim]):
    """Интерфейс сервиса для работы с страховыми случаями"""
    
    @abstractmethod
    def get_by_claim_number(self, claim_number: str) -> Optional[Claim]:
        """Получает страховой случай по номеру"""
        pass
    
    @abstractmethod
    def get_by_policy_id(self, policy_id: UUID, skip: int = 0, limit: int = 100) -> List[Claim]:
        """Получает список страховых случаев по полису"""
        pass
    
    @abstractmethod
    def get_by_client_id(self, client_id: UUID, skip: int = 0, limit: int = 100) -> List[Claim]:
        """Получает список страховых случаев клиента"""
        pass
    
    @abstractmethod
    def update_status(self, claim_id: UUID, status: ClaimStatus) -> Claim:
        """Обновляет статус страхового случая"""
        pass
    
    @abstractmethod
    def approve_claim(self, claim_id: UUID, approved_amount: float) -> Claim:
        """Утверждает страховой случай с указанной суммой выплаты"""
        pass
