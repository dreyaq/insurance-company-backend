from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from uuid import UUID

# Определяем обобщенный тип для сущности
T = TypeVar('T')


class BaseService(Generic[T], ABC):
    """Базовый интерфейс сервиса для доменных сущностей"""
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Создает новую сущность"""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Получает сущность по идентификатору"""
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Получает список сущностей с пагинацией"""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        """Обновляет существующую сущность"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: UUID) -> bool:
        """Удаляет сущность по идентификатору"""
        pass
