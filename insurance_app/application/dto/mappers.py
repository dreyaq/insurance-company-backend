from datetime import date
from typing import List, TypeVar, Generic, Type, Optional
from uuid import uuid4
from pydantic import BaseModel

from insurance_app.application.dto.client_dto import ClientCreateDTO, ClientUpdateDTO, ClientResponseDTO
from insurance_app.application.dto.policy_dto import PolicyCreateDTO, PolicyUpdateDTO, PolicyResponseDTO
from insurance_app.application.dto.claim_dto import ClaimCreateDTO, ClaimUpdateDTO, ClaimResponseDTO
from insurance_app.application.dto.payment_dto import PaymentCreateDTO, PaymentUpdateDTO, PaymentResponseDTO
from insurance_app.application.dto.user_dto import UserCreateDTO, UserUpdateDTO, UserResponseDTO
from insurance_app.domain.models.client import Client
from insurance_app.domain.models.policy import Policy, PolicyStatus
from insurance_app.domain.models.claim import Claim, ClaimStatus
from insurance_app.domain.models.payment import Payment, PaymentStatus
from insurance_app.domain.models.user import User


T = TypeVar('T')
U = TypeVar('U')


class Mapper(Generic[T, U]):
    """Базовый класс маппера для преобразования между доменными объектами и DTO"""
    
    @staticmethod
    def to_domain(dto: T, entity: Optional[U] = None) -> U:
        """Преобразует DTO в доменный объект"""
        raise NotImplementedError
    
    @staticmethod
    def to_dto(entity: U) -> T:
        """Преобразует доменный объект в DTO"""
        raise NotImplementedError
    
    @classmethod
    def to_domain_list(cls, dtos: List[T]) -> List[U]:
        """Преобразует список DTO в список доменных объектов"""
        return [cls.to_domain(dto) for dto in dtos]
    
    @classmethod
    def to_dto_list(cls, entities: List[U]) -> List[T]:
        """Преобразует список доменных объектов в список DTO"""
        return [cls.to_dto(entity) for entity in entities]


class ClientMapper:
    """Маппер для клиентов"""
    
    @staticmethod
    def to_domain(dto: ClientCreateDTO | ClientUpdateDTO, entity: Optional[Client] = None) -> Client:
        """Преобразует DTO клиента в доменный объект"""
        if entity is None:
            entity = Client()
        
        # Копируем все поля из DTO в доменный объект
        for field, value in dto.dict(exclude_unset=True).items():
            setattr(entity, field, value)
        
        return entity
    
    @staticmethod
    def to_dto(entity: Client) -> ClientResponseDTO:
        """Преобразует доменный объект клиента в DTO"""
        return ClientResponseDTO(
            id=entity.id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            email=entity.email,
            phone=entity.phone,
            birth_date=entity.birth_date,
            address=entity.address,
            passport_number=entity.passport_number,
            created_at=entity.created_at,
            is_active=entity.is_active
        )
    
    @classmethod
    def to_dto_list(cls, entities: List[Client]) -> List[ClientResponseDTO]:
        """Преобразует список доменных объектов в список DTO"""
        return [cls.to_dto(entity) for entity in entities]


class PolicyMapper:
    """Маппер для полисов"""
    
    @staticmethod
    def to_domain(dto: PolicyCreateDTO | PolicyUpdateDTO, entity: Optional[Policy] = None) -> Policy:
        """Преобразует DTO полиса в доменный объект"""
        if entity is None:
            entity = Policy()
        
        # Копируем все поля из DTO в доменный объект
        for field, value in dto.dict(exclude_unset=True).items():
            setattr(entity, field, value)
        
        return entity
    
    @staticmethod
    def to_dto(entity: Policy) -> PolicyResponseDTO:
        """Преобразует доменный объект полиса в DTO"""
        return PolicyResponseDTO(
            id=entity.id,
            policy_number=entity.policy_number,
            client_id=entity.client_id,
            type=entity.type,
            status=entity.status,
            start_date=entity.start_date,
            end_date=entity.end_date,
            coverage_amount=entity.coverage_amount,
            premium_amount=entity.premium_amount,
            payment_frequency=entity.payment_frequency,
            description=entity.description,
            created_at=entity.created_at,
            is_active=entity.is_active
        )
    
    @classmethod
    def to_dto_list(cls, entities: List[Policy]) -> List[PolicyResponseDTO]:
        """Преобразует список доменных объектов в список DTO"""
        return [cls.to_dto(entity) for entity in entities]


class ClaimMapper:
    """Маппер для страховых случаев"""
    
    @staticmethod
    def to_domain(dto: ClaimCreateDTO | ClaimUpdateDTO, entity: Optional[Claim] = None) -> Claim:
        """Преобразует DTO страхового случая в доменный объект"""
        if entity is None:
            entity = Claim()
        
        # Копируем все поля из DTO в доменный объект
        for field, value in dto.dict(exclude_unset=True).items():
            setattr(entity, field, value)
        
        return entity
    
    @staticmethod
    def to_dto(entity: Claim) -> ClaimResponseDTO:
        """Преобразует доменный объект страхового случая в DTO"""
        return ClaimResponseDTO(
            id=entity.id,
            claim_number=entity.claim_number,
            policy_id=entity.policy_id,
            client_id=entity.client_id,
            incident_date=entity.incident_date,
            report_date=entity.report_date,
            description=entity.description,
            status=entity.status,
            claim_amount=entity.claim_amount,
            approved_amount=entity.approved_amount,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_active=entity.is_active
        )
    
    @classmethod
    def to_dto_list(cls, entities: List[Claim]) -> List[ClaimResponseDTO]:
        """Преобразует список доменных объектов в список DTO"""
        return [cls.to_dto(entity) for entity in entities]


class PaymentMapper:
    """Маппер для платежей"""
    
    @staticmethod
    def to_domain(dto: PaymentCreateDTO | PaymentUpdateDTO, entity: Optional[Payment] = None) -> Payment:
        """Преобразует DTO платежа в доменный объект"""
        if entity is None:
            entity = Payment()
        
        # Копируем все поля из DTO в доменный объект
        for field, value in dto.dict(exclude_unset=True).items():
            setattr(entity, field, value)
        
        return entity
    
    @staticmethod
    def to_dto(entity: Payment) -> PaymentResponseDTO:
        """Преобразует доменный объект платежа в DTO"""
        return PaymentResponseDTO(
            id=entity.id,
            payment_number=entity.payment_number,
            client_id=entity.client_id,
            policy_id=entity.policy_id,
            claim_id=entity.claim_id,
            amount=entity.amount,
            payment_date=entity.payment_date,
            due_date=entity.due_date,
            status=entity.status,
            payment_type=entity.payment_type,
            payment_method=entity.payment_method,
            description=entity.description,
            created_at=entity.created_at,
            is_active=entity.is_active
        )
    
    @classmethod
    def to_dto_list(cls, entities: List[Payment]) -> List[PaymentResponseDTO]:
        """Преобразует список доменных объектов в список DTO"""
        return [cls.to_dto(entity) for entity in entities]


class UserMapper:
    """Маппер для пользователей"""
    
    @staticmethod
    def to_domain(dto: UserCreateDTO | UserUpdateDTO, entity: Optional[User] = None) -> User:
        """Преобразует DTO пользователя в доменный объект"""
        if entity is None:
            entity = User()
        
        # Копируем все поля из DTO в доменный объект (кроме пароля)
        dto_dict = dto.dict(exclude_unset=True)
        
        # Удаляем пароль, так как его нужно обрабатывать отдельно
        if "password" in dto_dict:
            dto_dict.pop("password")
            
        for field, value in dto_dict.items():
            setattr(entity, field, value)
        
        return entity
    
    @staticmethod
    def to_dto(entity: User) -> UserResponseDTO:
        """Преобразует доменный объект пользователя в DTO"""
        return UserResponseDTO(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            full_name=entity.full_name,
            is_active=entity.is_active,
            is_superuser=entity.is_superuser,
            roles=entity.roles,
            created_at=entity.created_at
        )
    
    @classmethod
    def to_dto_list(cls, entities: List[User]) -> List[UserResponseDTO]:
        """Преобразует список доменных объектов в список DTO"""
        return [cls.to_dto(entity) for entity in entities]
