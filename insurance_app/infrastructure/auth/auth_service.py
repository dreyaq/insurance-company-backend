from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from uuid import UUID

from insurance_app.domain.models.user import User
from insurance_app.domain.exceptions import AuthenticationException


class AuthService:
    """Сервис для аутентификации и авторизации пользователей"""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def create_password_hash(self, password: str) -> str:
        """Создает хеш пароля"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет соответствие пароля хешу"""
        return self.pwd_context.verify(plain_password, hashed_password)
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, user: User) -> str:
        """Создает JWT токен для пользователя"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "roles": user.roles,
            "is_superuser": user.is_superuser,
            "exp": expire
        }
        
        print(f"Creating token with payload: {to_encode}")
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Декодирует JWT токен"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationException("Токен истек")
        except jwt.InvalidTokenError:
            raise AuthenticationException("Недействительный токен")
    
    def get_current_user_id(self, token: str) -> UUID:
        """Получает ID пользователя из токена"""
        payload = self.decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("Недействительный токен (отсутствует ID пользователя)")
        return UUID(user_id)
    
    def is_token_valid(self, token: str) -> bool:
        """Проверяет валидность токена"""
        try:
            self.decode_token(token)
            return True
        except:
            return False
    
    def has_role(self, token: str, required_role: str) -> bool:
        """Проверяет наличие роли у пользователя"""
        try:
            payload = self.decode_token(token)
            roles = payload.get("roles", [])
            is_superuser = payload.get("is_superuser", False)
            
            # Суперпользователи имеют доступ ко всему
            if is_superuser:
                return True
            
            return required_role in roles
        except:
            return False
