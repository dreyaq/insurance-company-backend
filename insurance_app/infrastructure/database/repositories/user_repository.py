from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from insurance_app.domain.models.user import User
from insurance_app.domain.repositories.user_repository import UserRepository
from insurance_app.infrastructure.database.models.user import UserModel


class UserRepositoryImpl(UserRepository):
    """Реализация репозитория для работы с пользователями"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, user: User) -> User:
        user_model = UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            roles=user.roles,
            created_at=user.created_at
        )
        
        self.session.add(user_model)
        self.session.commit()
        self.session.refresh(user_model)
        
        return self._map_to_domain(user_model)
    
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        user_model = self.session.get(UserModel, user_id)
        
        if not user_model:
            return None
        
        return self._map_to_domain(user_model)
    
    def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.username == username)
        user_model = self.session.execute(stmt).scalar_one_or_none()
        
        if not user_model:
            return None
        
        return self._map_to_domain(user_model)
    
    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email)
        user_model = self.session.execute(stmt).scalar_one_or_none()
        
        if not user_model:
            return None
        
        return self._map_to_domain(user_model)
    
    def update(self, user: User) -> User:
        user_model = self.session.get(UserModel, user.id)
        
        if not user_model:
            raise ValueError(f"User with ID {user.id} not found")
        
        user_model.username = user.username
        user_model.email = user.email
        user_model.full_name = user.full_name
        user_model.hashed_password = user.hashed_password
        user_model.is_active = user.is_active
        user_model.is_superuser = user.is_superuser
        user_model.roles = user.roles
        
        self.session.commit()
        self.session.refresh(user_model)
        
        return self._map_to_domain(user_model)
    
    def delete(self, user_id: UUID) -> bool:
        user_model = self.session.get(UserModel, user_id)
        
        if not user_model:
            return False
        
        self.session.delete(user_model)
        self.session.commit()
        
        return True
    
    def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        stmt = select(UserModel).offset(skip).limit(limit)
        user_models = self.session.execute(stmt).scalars().all()
        
        return [self._map_to_domain(user_model) for user_model in user_models]
    
    def _map_to_domain(self, user_model: UserModel) -> User:
        """Преобразует ORM модель в доменную модель"""
        return User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
            full_name=user_model.full_name,
            hashed_password=user_model.hashed_password,
            is_active=user_model.is_active,
            is_superuser=user_model.is_superuser,
            roles=user_model.roles,
            created_at=user_model.created_at
        )
