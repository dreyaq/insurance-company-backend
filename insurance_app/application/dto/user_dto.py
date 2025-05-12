from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class UserBaseDTO(BaseModel):
    """Базовый DTO для пользователя"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)


class UserCreateDTO(UserBaseDTO):
    """DTO для создания пользователя"""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdateDTO(BaseModel):
    """DTO для обновления пользователя"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None
    roles: Optional[List[str]] = None


class UserResponseDTO(UserBaseDTO):
    """DTO для ответа с информацией о пользователе"""
    id: UUID
    is_active: bool
    is_superuser: bool
    roles: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenDTO(BaseModel):
    """DTO для токена доступа"""
    access_token: str
    token_type: str = "bearer"
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None


class LoginDTO(BaseModel):
    """DTO для входа в систему"""
    username: str
    password: str
