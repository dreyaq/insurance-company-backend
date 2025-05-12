from abc import abstractmethod
from typing import Optional, List
from uuid import UUID

from insurance_app.application.interfaces.base_repository import BaseRepository
from insurance_app.domain.models.claim import Claim


class ClaimRepository(BaseRepository[Claim]):
    """Интерфейс репозитория для работы с страховыми случаями"""
    
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