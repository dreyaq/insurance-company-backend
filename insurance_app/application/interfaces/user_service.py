from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from insurance_app.domain.models.user import User


class UserService(ABC):
    """Интерфейс сервиса для работы с пользователями"""
    
    @abstractmethod
    def register_user(self, username: str, email: str, password: str, full_name: Optional[str] = None) -> User:
        """Регистрация нового пользователя"""
        pass
    
    @abstractmethod
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        pass
    
    @abstractmethod
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Получение пользователя по ID"""
        pass
    
    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по имени пользователя"""
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        pass
    
    @abstractmethod
    def update_user(self, user_id: UUID, user_data: dict) -> User:
        """Обновление данных пользователя"""
        pass
    
    @abstractmethod
    def delete_user(self, user_id: UUID) -> bool:
        """Удаление пользователя"""
        pass
    
    @abstractmethod
    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка пользователей с пагинацией"""
        pass
    
    @abstractmethod
    def change_password(self, user_id: UUID, current_password: str, new_password: str) -> bool:
        """Изменение пароля пользователя"""
        pass
    
    @abstractmethod
    def update_user_roles(self, user_id: UUID, roles: List[str]) -> User:
        """Обновление ролей пользователя"""
        pass
