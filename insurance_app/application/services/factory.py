from sqlalchemy.orm import Session
import os

from insurance_app.application.interfaces.client_service import ClientService
from insurance_app.application.interfaces.policy_service import PolicyService
from insurance_app.application.interfaces.claim_service import ClaimService
from insurance_app.application.interfaces.payment_service import PaymentService
from insurance_app.application.interfaces.user_service import UserService
from insurance_app.application.services import (
    ClientServiceImpl,
    PolicyServiceImpl,
    ClaimServiceImpl,
    PaymentServiceImpl,
    UserServiceImpl
)
from insurance_app.infrastructure.database.repositories.factory import RepositoryFactory
from insurance_app.infrastructure.auth.auth_service import AuthService


class ServiceFactory:
    """Фабрика для создания сервисов"""
    
    @staticmethod
    def create_client_service(session: Session) -> ClientService:
        """Создает сервис для работы с клиентами"""
        client_repository = RepositoryFactory.create_client_repository(session)
        return ClientServiceImpl(client_repository)
    
    @staticmethod
    def create_policy_service(session: Session) -> PolicyService:
        """Создает сервис для работы с полисами"""
        policy_repository = RepositoryFactory.create_policy_repository(session)
        client_repository = RepositoryFactory.create_client_repository(session)
        return PolicyServiceImpl(policy_repository, client_repository)
    
    @staticmethod
    def create_claim_service(session: Session) -> ClaimService:
        """Создает сервис для работы с страховыми случаями"""
        claim_repository = RepositoryFactory.create_claim_repository(session)
        policy_repository = RepositoryFactory.create_policy_repository(session)
        client_repository = RepositoryFactory.create_client_repository(session)
        return ClaimServiceImpl(claim_repository, policy_repository, client_repository)
    
    @staticmethod
    def create_payment_service(session: Session) -> PaymentService:
        """Создает сервис для работы с платежами"""
        payment_repository = RepositoryFactory.create_payment_repository(session)
        policy_repository = RepositoryFactory.create_policy_repository(session)
        claim_repository = RepositoryFactory.create_claim_repository(session)
        client_repository = RepositoryFactory.create_client_repository(session)
        return PaymentServiceImpl(
            payment_repository,
            policy_repository,
            claim_repository,
            client_repository
        )
        
    @staticmethod
    def create_user_service(session: Session) -> UserService:
        """Создает сервис для работы с пользователями"""
        user_repository = RepositoryFactory.create_user_repository(session)
        # Получаем секретный ключ из переменных окружения
        secret_key = os.environ.get("SECRET_KEY", "your-secret-key")
        auth_service = AuthService(secret_key=secret_key)
        return UserServiceImpl(user_repository, auth_service)
