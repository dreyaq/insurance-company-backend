from sqlalchemy.orm import Session

from insurance_app.application.interfaces.client_repository import ClientRepository
from insurance_app.application.interfaces.policy_repository import PolicyRepository
from insurance_app.application.interfaces.claim_repository import ClaimRepository
from insurance_app.application.interfaces.payment_repository import PaymentRepository
from insurance_app.domain.repositories.user_repository import UserRepository
from insurance_app.infrastructure.database.repositories import (
    ClientRepositoryImpl,
    PolicyRepositoryImpl,
    ClaimRepositoryImpl,
    PaymentRepositoryImpl
)
from insurance_app.infrastructure.database.repositories.user_repository import UserRepositoryImpl


class RepositoryFactory:
    """Фабрика для создания репозиториев"""
    
    @staticmethod
    def create_client_repository(session: Session) -> ClientRepository:
        """Создает репозиторий для работы с клиентами"""
        return ClientRepositoryImpl(session)
    
    @staticmethod
    def create_policy_repository(session: Session) -> PolicyRepository:
        """Создает репозиторий для работы с полисами"""
        return PolicyRepositoryImpl(session)
    
    @staticmethod
    def create_claim_repository(session: Session) -> ClaimRepository:
        """Создает репозиторий для работы с страховыми случаями"""
        return ClaimRepositoryImpl(session)
    
    @staticmethod
    def create_payment_repository(session: Session) -> PaymentRepository:
        """Создает репозиторий для работы с платежами"""
        return PaymentRepositoryImpl(session)
    
    @staticmethod
    def create_user_repository(session: Session) -> UserRepository:
        """Создает репозиторий для работы с пользователями"""
        return UserRepositoryImpl(session)
