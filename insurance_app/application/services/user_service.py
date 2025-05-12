from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from insurance_app.application.interfaces.user_service import UserService
from insurance_app.domain.models.user import User
from insurance_app.domain.repositories.user_repository import UserRepository
from insurance_app.infrastructure.auth.auth_service import AuthService
from insurance_app.domain.exceptions import EntityNotFoundException, AuthenticationException, BusinessRuleViolationException


class UserServiceImpl(UserService):
    """Реализация сервиса для работы с пользователями"""
    
    def __init__(self, user_repository: UserRepository, auth_service: AuthService):
        self.user_repository = user_repository
        self.auth_service = auth_service
    
    def register_user(self, username: str, email: str, password: str, full_name: Optional[str] = None) -> User:
        """Регистрация нового пользователя"""
        # Проверяем, что пользователь с таким username не существует
        existing_user = self.user_repository.get_by_username(username)
        if existing_user:
            raise BusinessRuleViolationException(f"Пользователь с именем {username} уже существует")
        
        # Проверяем, что пользователь с таким email не существует
        existing_user = self.user_repository.get_by_email(email)
        if existing_user:
            raise BusinessRuleViolationException(f"Пользователь с email {email} уже существует")
        
        # Создаем нового пользователя
        hashed_password = self.auth_service.create_password_hash(password)
        
        user = User(
            id=uuid4(),
            username=username,
            email=email,
            full_name=full_name or "",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
            roles=["user"],
            created_at=datetime.utcnow()
        )
        
        return self.user_repository.create(user)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        # Получаем пользователя по username
        user = self.user_repository.get_by_username(username)
        
        # Если пользователь не найден, возвращаем None
        if not user:
            return None
        
        # Если пользователь не активен, возвращаем None
        if not user.is_active:
            return None
        
        # Проверяем пароль
        if not self.auth_service.verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Получение пользователя по ID"""
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            raise EntityNotFoundException(entity_type="User", entity_id=str(user_id))
        
        return user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по имени пользователя"""
        return self.user_repository.get_by_username(username)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        return self.user_repository.get_by_email(email)
    
    def update_user(self, user_id: UUID, user_data: dict) -> User:
        """Обновление данных пользователя"""
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            raise EntityNotFoundException(entity_type="User", entity_id=str(user_id))
        
        # Проверяем, что пользователь с таким username не существует
        if "username" in user_data and user_data["username"] != user.username:
            existing_user = self.user_repository.get_by_username(user_data["username"])
            if existing_user:
                raise BusinessRuleViolationException(f"Пользователь с именем {user_data['username']} уже существует")
        
        # Проверяем, что пользователь с таким email не существует
        if "email" in user_data and user_data["email"] != user.email:
            existing_user = self.user_repository.get_by_email(user_data["email"])
            if existing_user:
                raise BusinessRuleViolationException(f"Пользователь с email {user_data['email']} уже существует")
        
        # Обновляем поля пользователя
        for key, value in user_data.items():
            if hasattr(user, key) and key != "id" and key != "hashed_password":
                setattr(user, key, value)
        
        return self.user_repository.update(user)
    
    def delete_user(self, user_id: UUID) -> bool:
        """Удаление пользователя"""
        return self.user_repository.delete(user_id)
    
    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка пользователей с пагинацией"""
        return self.user_repository.list(skip, limit)
    
    def change_password(self, user_id: UUID, current_password: str, new_password: str) -> bool:
        """Изменение пароля пользователя"""
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            raise EntityNotFoundException(entity_type="User", entity_id=str(user_id))
        
        # Проверяем текущий пароль
        if not self.auth_service.verify_password(current_password, user.hashed_password):
            raise AuthenticationException("Неверный пароль")
        
        # Обновляем пароль
        user.hashed_password = self.auth_service.create_password_hash(new_password)
        
        self.user_repository.update(user)
        
        return True
    
    def update_user_roles(self, user_id: UUID, roles: List[str]) -> User:
        """Обновление ролей пользователя"""
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            raise EntityNotFoundException(entity_type="User", entity_id=str(user_id))
        
        user.roles = roles
        
        return self.user_repository.update(user)
