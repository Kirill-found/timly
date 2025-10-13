"""
Pydantic схемы для пользователей
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, UUID4


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    company_name: Optional[str] = None


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str = Field(..., min_length=6, description="Пароль минимум 6 символов")


class UserLogin(BaseModel):
    """Схема для входа"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    company_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)


class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""
    id: UUID4
    token_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Схема ответа с токеном"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class HHTokenUpdate(BaseModel):
    """Схема для обновления HH.ru токена"""
    hh_token: str = Field(..., description="Токен доступа к HH.ru API")