from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from insurance_app.domain.models.user import User


class UserRepository(ABC):
    """Интерфейс репозитория для работы с пользователями"""
    
    @abstractmethod
    def create(self, user: User) -> User:
        """Создание нового пользователя"""
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Получение пользователя по ID"""
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по имени пользователя"""
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        pass
    
    @abstractmethod
    def update(self, user: User) -> User:
        """Обновление данных пользователя"""
        pass
    
    @abstractmethod
    def delete(self, user_id: UUID) -> bool:
        """Удаление пользователя"""
        pass
    
    @abstractmethod
    def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка пользователей с пагинацией"""
        pass
