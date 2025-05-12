from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os

from insurance_app.application.interfaces.client_service import ClientService
from insurance_app.application.interfaces.policy_service import PolicyService
from insurance_app.application.interfaces.claim_service import ClaimService
from insurance_app.application.interfaces.payment_service import PaymentService
from insurance_app.application.interfaces.user_service import UserService
from insurance_app.application.services.factory import ServiceFactory
from insurance_app.infrastructure.database.config import get_db
from insurance_app.infrastructure.auth.auth_service import AuthService
from insurance_app.domain.exceptions import AuthenticationException

# Создаем объект для OAuth2 с использованием пароля
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_client_service(db: Session = Depends(get_db)) -> ClientService:
    """Получает сервис для работы с клиентами"""
    return ServiceFactory.create_client_service(db)


def get_policy_service(db: Session = Depends(get_db)) -> PolicyService:
    """Получает сервис для работы с полисами"""
    return ServiceFactory.create_policy_service(db)


def get_claim_service(db: Session = Depends(get_db)) -> ClaimService:
    """Получает сервис для работы с страховыми случаями"""
    return ServiceFactory.create_claim_service(db)


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    """Получает сервис для работы с платежами"""
    return ServiceFactory.create_payment_service(db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Получает сервис для работы с пользователями"""
    return ServiceFactory.create_user_service(db)


def get_auth_service() -> AuthService:
    """Получает сервис для аутентификации"""
    secret_key = os.environ.get("SECRET_KEY", "your-secret-key")
    return AuthService(secret_key=secret_key)


def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Получает ID текущего пользователя из токена"""
    try:
        return auth_service.get_current_user_id(token)
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service)
):
    """Получает текущего пользователя из токена"""
    user_id = get_current_user_id(token, auth_service)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь неактивен",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user
