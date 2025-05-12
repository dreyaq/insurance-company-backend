import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from insurance_app.application.interfaces.claim_repository import ClaimRepository
from insurance_app.application.interfaces.claim_service import ClaimService
from insurance_app.application.interfaces.policy_repository import PolicyRepository
from insurance_app.application.interfaces.client_repository import ClientRepository
from insurance_app.domain.models.claim import Claim, ClaimStatus
from insurance_app.domain.models.policy import PolicyStatus


class ClaimServiceImpl(ClaimService):
    """Реализация сервиса для работы с страховыми случаями"""
    
    def __init__(
        self,
        claim_repository: ClaimRepository,
        policy_repository: PolicyRepository,
        client_repository: ClientRepository
    ):
        self.claim_repository = claim_repository
        self.policy_repository = policy_repository
        self.client_repository = client_repository
    
    def create(self, entity: Claim) -> Claim:
        """Создает новый страховой случай"""
        # Генерируем ID если его нет
        if entity.id is None:
            entity.id = uuid.uuid4()
        
        # Генерируем номер страхового случая если его нет
        if not entity.claim_number:
            entity.claim_number = f"CLM-{str(entity.id)[:8].upper()}"
        
        # Устанавливаем даты
        today = date.today()
        if entity.created_at is None:
            entity.created_at = today
        
        if entity.updated_at is None:
            entity.updated_at = today
        
        if entity.report_date is None:
            entity.report_date = today
        
        # Проверяем существование полиса
        if entity.policy_id:
            policy = self.policy_repository.get_by_id(entity.policy_id)
            if not policy:
                raise ValueError(f"Полис с ID {entity.policy_id} не найден")
            
            # Проверяем что полис активен
            if policy.status != PolicyStatus.ACTIVE:
                raise ValueError(f"Полис {policy.policy_number} не активен")
            
            # Проверяем что страховой случай произошел в период действия полиса
            if entity.incident_date:
                if policy.start_date and entity.incident_date < policy.start_date:
                    raise ValueError("Дата страхового случая раньше даты начала действия полиса")
                
                if policy.end_date and entity.incident_date > policy.end_date:
                    raise ValueError("Дата страхового случая позже даты окончания действия полиса")
            
            # Если клиент не указан, берем его из полиса
            if entity.client_id is None and policy.client_id:
                entity.client_id = policy.client_id
        
        # Проверяем существование клиента
        if entity.client_id:
            client = self.client_repository.get_by_id(entity.client_id)
            if not client:
                raise ValueError(f"Клиент с ID {entity.client_id} не найден")
        
        return self.claim_repository.create(entity)
    
    def get_by_id(self, entity_id: UUID) -> Optional[Claim]:
        """Получает страховой случай по идентификатору"""
        return self.claim_repository.get_by_id(entity_id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Claim]:
        """Получает список страховых случаев с пагинацией"""
        return self.claim_repository.get_all(skip, limit)
    
    def update(self, entity: Claim) -> Claim:
        """Обновляет существующий страховой случай"""
        entity.updated_at = date.today()
        return self.claim_repository.update(entity)
    
    def delete(self, entity_id: UUID) -> bool:
        """Удаляет страховой случай по идентификатору"""
        return self.claim_repository.delete(entity_id)
    
    def get_by_claim_number(self, claim_number: str) -> Optional[Claim]:
        """Получает страховой случай по номеру"""
        return self.claim_repository.get_by_claim_number(claim_number)
    
    def get_by_policy_id(self, policy_id: UUID, skip: int = 0, limit: int = 100) -> List[Claim]:
        """Получает список страховых случаев по полису"""
        return self.claim_repository.get_by_policy_id(policy_id, skip, limit)
    
    def get_by_client_id(self, client_id: UUID, skip: int = 0, limit: int = 100) -> List[Claim]:
        """Получает список страховых случаев клиента"""
        return self.claim_repository.get_by_client_id(client_id, skip, limit)
    
    def update_status(self, claim_id: UUID, status: ClaimStatus) -> Claim:
        """Обновляет статус страхового случая"""
        claim = self.claim_repository.get_by_id(claim_id)
        if not claim:
            raise ValueError(f"Страховой случай с ID {claim_id} не найден")
        
        claim.status = status
        claim.updated_at = date.today()
        
        return self.claim_repository.update(claim)
    
    def approve_claim(self, claim_id: UUID, approved_amount: float) -> Claim:
        """Утверждает страховой случай с указанной суммой выплаты"""
        claim = self.claim_repository.get_by_id(claim_id)
        if not claim:
            raise ValueError(f"Страховой случай с ID {claim_id} не найден")
        
        # Проверка что сумма выплаты не превышает сумму запроса
        if Decimal(str(approved_amount)) > claim.claim_amount:
            raise ValueError("Сумма выплаты не может превышать сумму страхового случая")
        
        # Проверка на действующий полис
        if claim.policy_id:
            policy = self.policy_repository.get_by_id(claim.policy_id)
            if not policy:
                raise ValueError(f"Полис с ID {claim.policy_id} не найден")
            
            # Проверка что сумма выплаты не превышает страховую сумму
            if Decimal(str(approved_amount)) > policy.coverage_amount:
                raise ValueError("Сумма выплаты не может превышать страховую сумму полиса")
        
        claim.approved_amount = Decimal(str(approved_amount))
        claim.status = ClaimStatus.APPROVED
        claim.updated_at = date.today()
        
        return self.claim_repository.update(claim)
