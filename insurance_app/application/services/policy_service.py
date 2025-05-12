import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from insurance_app.application.interfaces.policy_repository import PolicyRepository
from insurance_app.application.interfaces.policy_service import PolicyService
from insurance_app.application.interfaces.client_repository import ClientRepository
from insurance_app.domain.models.policy import Policy, PolicyType, PolicyStatus


class PolicyServiceImpl(PolicyService):
    """Реализация сервиса для работы с полисами"""
    
    def __init__(self, policy_repository: PolicyRepository, client_repository: ClientRepository):
        self.policy_repository = policy_repository
        self.client_repository = client_repository
    
    def create(self, entity: Policy) -> Policy:
        """Создает новый полис"""
        if entity.id is None:
            entity.id = uuid.uuid4()
        
        if not entity.policy_number:
            entity.policy_number = f"POL-{str(entity.id)[:8].upper()}"
        
        if entity.created_at is None:
            entity.created_at = date.today()
        
        if entity.client_id:
            client = self.client_repository.get_by_id(entity.client_id)
            if not client:
                raise ValueError(f"Клиент с ID {entity.client_id} не найден")
        
        if entity.premium_amount == Decimal("0.00"):
            entity = self.calculate_premium(entity)
        
        return self.policy_repository.create(entity)
    
    def get_by_id(self, entity_id: UUID) -> Optional[Policy]:
        """Получает полис по идентификатору"""
        return self.policy_repository.get_by_id(entity_id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Policy]:
        """Получает список полисов с пагинацией"""
        return self.policy_repository.get_all(skip, limit)
    
    def update(self, entity: Policy) -> Policy:
        """Обновляет существующий полис"""
        return self.policy_repository.update(entity)
    
    def delete(self, entity_id: UUID) -> bool:
        """Удаляет полис по идентификатору"""
        return self.policy_repository.delete(entity_id)
    
    def get_by_policy_number(self, policy_number: str) -> Optional[Policy]:
        """Получает полис по номеру"""
        return self.policy_repository.get_by_policy_number(policy_number)
    
    def get_by_client_id(self, client_id: UUID, skip: int = 0, limit: int = 100) -> List[Policy]:
        """Получает список полисов клиента"""
        return self.policy_repository.get_by_client_id(client_id, skip, limit)
    
    def get_active_policies(self, skip: int = 0, limit: int = 100) -> List[Policy]:
        """Получает список активных полисов"""
        return self.policy_repository.get_active_policies(skip, limit)
    
    def calculate_premium(self, policy: Policy) -> Policy:
        """Рассчитывает страховую премию для полиса"""
        base_rate = Decimal("0.05") 
        
        type_coefficients = {
            PolicyType.LIFE: Decimal("1.5"),
            PolicyType.HEALTH: Decimal("1.2"),
            PolicyType.PROPERTY: Decimal("0.8"),
            PolicyType.VEHICLE: Decimal("1.0"),
            PolicyType.TRAVEL: Decimal("0.6"),
        }
        
        coefficient = type_coefficients.get(policy.type, Decimal("1.0"))
        
        premium = policy.coverage_amount * base_rate * coefficient
        
        premium = premium.quantize(Decimal("0.01"))
        
        policy.premium_amount = premium
        
        return policy
