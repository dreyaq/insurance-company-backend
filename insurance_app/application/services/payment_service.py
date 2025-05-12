import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from insurance_app.application.interfaces.payment_repository import PaymentRepository
from insurance_app.application.interfaces.payment_service import PaymentService
from insurance_app.application.interfaces.policy_repository import PolicyRepository
from insurance_app.application.interfaces.claim_repository import ClaimRepository
from insurance_app.application.interfaces.client_repository import ClientRepository
from insurance_app.domain.models.payment import Payment, PaymentStatus, PaymentType
from insurance_app.domain.models.claim import ClaimStatus


class PaymentServiceImpl(PaymentService):
    """Реализация сервиса для работы с платежами"""
    
    def __init__(
        self,
        payment_repository: PaymentRepository,
        policy_repository: PolicyRepository,
        claim_repository: ClaimRepository,
        client_repository: ClientRepository
    ):
        self.payment_repository = payment_repository
        self.policy_repository = policy_repository
        self.claim_repository = claim_repository
        self.client_repository = client_repository
    
    def create(self, entity: Payment) -> Payment:
        """Создает новый платеж"""
        # Генерируем ID если его нет
        if entity.id is None:
            entity.id = uuid.uuid4()
        
        # Генерируем номер платежа если его нет
        if not entity.payment_number:
            entity.payment_number = f"PAY-{str(entity.id)[:8].upper()}"
        
        # Устанавливаем дату создания
        if entity.created_at is None:
            entity.created_at = date.today()
        
        # Проверяем существование клиента
        if entity.client_id:
            client = self.client_repository.get_by_id(entity.client_id)
            if not client:
                raise ValueError(f"Клиент с ID {entity.client_id} не найден")
        
        # Проверяем существование полиса если указан
        if entity.policy_id:
            policy = self.policy_repository.get_by_id(entity.policy_id)
            if not policy:
                raise ValueError(f"Полис с ID {entity.policy_id} не найден")
            
            # Если клиент не указан, берем его из полиса
            if entity.client_id is None and policy.client_id:
                entity.client_id = policy.client_id
        
        # Проверяем существование страхового случая если указан
        if entity.claim_id:
            claim = self.claim_repository.get_by_id(entity.claim_id)
            if not claim:
                raise ValueError(f"Страховой случай с ID {entity.claim_id} не найден")
            
            # Если клиент не указан, берем его из страхового случая
            if entity.client_id is None and claim.client_id:
                entity.client_id = claim.client_id
            
            # Если полис не указан, берем его из страхового случая
            if entity.policy_id is None and claim.policy_id:
                entity.policy_id = claim.policy_id
        
        return self.payment_repository.create(entity)
    
    def get_by_id(self, entity_id: UUID) -> Optional[Payment]:
        """Получает платеж по идентификатору"""
        return self.payment_repository.get_by_id(entity_id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Получает список платежей с пагинацией"""
        return self.payment_repository.get_all(skip, limit)
    
    def update(self, entity: Payment) -> Payment:
        """Обновляет существующий платеж"""
        return self.payment_repository.update(entity)
    
    def delete(self, entity_id: UUID) -> bool:
        """Удаляет платеж по идентификатору"""
        return self.payment_repository.delete(entity_id)
    
    def get_by_payment_number(self, payment_number: str) -> Optional[Payment]:
        """Получает платеж по номеру"""
        return self.payment_repository.get_by_payment_number(payment_number)
    
    def get_by_client_id(self, client_id: UUID, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Получает список платежей клиента"""
        return self.payment_repository.get_by_client_id(client_id, skip, limit)
    
    def get_by_policy_id(self, policy_id: UUID, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Получает список платежей по полису"""
        return self.payment_repository.get_by_policy_id(policy_id, skip, limit)
    
    def get_by_claim_id(self, claim_id: UUID, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Получает список платежей по страховому случаю"""
        return self.payment_repository.get_by_claim_id(claim_id, skip, limit)
    
    def process_payment(self, payment_id: UUID, payment_date: date = None) -> Payment:
        """Обрабатывает платеж, меняя его статус на COMPLETED"""
        payment = self.payment_repository.get_by_id(payment_id)
        if not payment:
            raise ValueError(f"Платеж с ID {payment_id} не найден")
        
        # Устанавливаем дату платежа если не указана
        if payment_date is None:
            payment_date = date.today()
        
        payment.payment_date = payment_date
        payment.status = PaymentStatus.COMPLETED
        
        return self.payment_repository.update(payment)
    
    def create_premium_payment(self, policy_id: UUID) -> Payment:
        """Создает платеж страховой премии для полиса"""
        policy = self.policy_repository.get_by_id(policy_id)
        if not policy:
            raise ValueError(f"Полис с ID {policy_id} не найден")
        
        # Создаем платеж
        payment = Payment(
            policy_id=policy.id,
            client_id=policy.client_id,
            amount=policy.premium_amount,
            payment_type=PaymentType.PREMIUM,
            status=PaymentStatus.PENDING,
            due_date=date.today(),  # Обычно устанавливается на будущую дату
            description=f"Страховая премия по полису {policy.policy_number}"
        )
        
        return self.create(payment)
    
    def create_claim_payout(self, claim_id: UUID) -> Payment:
        """Создает платеж страховой выплаты по страховому случаю"""
        claim = self.claim_repository.get_by_id(claim_id)
        if not claim:
            raise ValueError(f"Страховой случай с ID {claim_id} не найден")
        
        # Проверяем что страховой случай утвержден
        if claim.status != ClaimStatus.APPROVED:
            raise ValueError("Страховой случай должен быть утвержден для создания выплаты")
        
        # Проверяем что сумма утверждена
        if claim.approved_amount is None:
            raise ValueError("Сумма выплаты не установлена")
        
        # Создаем платеж
        payment = Payment(
            claim_id=claim.id,
            policy_id=claim.policy_id,
            client_id=claim.client_id,
            amount=claim.approved_amount,
            payment_type=PaymentType.CLAIM_PAYOUT,
            status=PaymentStatus.PENDING,
            description=f"Страховая выплата по страховому случаю {claim.claim_number}"
        )
        
        return self.create(payment)
