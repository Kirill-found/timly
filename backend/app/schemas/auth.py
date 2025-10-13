"""
Pydantic схемы для аутентификации
Валидация данных регистрации, логина и профиля
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re


class UserRegistration(BaseModel):
    """Схема регистрации нового пользователя"""
    email: EmailStr = Field(..., description="Email адрес пользователя")
    password: str = Field(..., min_length=8, max_length=100, description="Пароль (минимум 8 символов)")
    company_name: Optional[str] = Field(None, max_length=255, description="Название компании")

    @validator('password')
    def validate_password(cls, v):
        """Валидация сложности пароля"""
        if not re.search(r"[A-Z]", v):
            raise ValueError('Пароль должен содержать заглавную букву')
        if not re.search(r"[a-z]", v):
            raise ValueError('Пароль должен содержать строчную букву')
        if not re.search(r"\d", v):
            raise ValueError('Пароль должен содержать цифру')
        return v

    class Config:
        schema_extra = {
            "example": {
                "email": "hr@company.ru",
                "password": "SecurePass123",
                "company_name": "ООО Рога и Копыта"
            }
        }


class UserLogin(BaseModel):
    """Схема входа в систему"""
    email: EmailStr = Field(..., description="Email адрес")
    password: str = Field(..., description="Пароль")

    class Config:
        schema_extra = {
            "example": {
                "email": "hr@company.ru",
                "password": "SecurePass123"
            }
        }


class Token(BaseModel):
    """JWT токен ответ"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни access токена в секундах")

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }


class UserProfile(BaseModel):
    """Профиль пользователя для API ответов"""
    id: str = Field(..., description="UUID пользователя")
    email: EmailStr = Field(..., description="Email адрес")
    role: str = Field(..., description="Роль пользователя")
    company_name: Optional[str] = Field(None, description="Название компании")
    has_hh_token: bool = Field(..., description="Есть ли подтвержденный HH.ru токен")
    token_verified: bool = Field(..., description="Подтвержден ли токен")
    created_at: Optional[str] = Field(None, description="Дата регистрации")

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "hr@company.ru",
                "role": "user",
                "company_name": "ООО Рога и Копыта",
                "has_hh_token": True,
                "token_verified": True,
                "created_at": "2024-01-01T00:00:00"
            }
        }


class HHTokenUpdate(BaseModel):
    """Схема для обновления HH.ru токена"""
    hh_token: str = Field(..., min_length=10, description="API токен от HH.ru")

    @validator('hh_token')
    def validate_hh_token(cls, v):
        """Базовая валидация HH.ru токена"""
        if not v.strip():
            raise ValueError('HH.ru токен не может быть пустым')
        # TODO: Добавить более строгую валидацию формата токена
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "hh_token": "hh_access_token_here"
            }
        }


class PasswordChange(BaseModel):
    """Схема смены пароля"""
    current_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(..., min_length=8, max_length=100, description="Новый пароль")

    @validator('new_password')
    def validate_new_password(cls, v):
        """Валидация нового пароля"""
        if not re.search(r"[A-Z]", v):
            raise ValueError('Новый пароль должен содержать заглавную букву')
        if not re.search(r"[a-z]", v):
            raise ValueError('Новый пароль должен содержать строчную букву')
        if not re.search(r"\d", v):
            raise ValueError('Новый пароль должен содержать цифру')
        return v

    class Config:
        schema_extra = {
            "example": {
                "current_password": "OldPass123",
                "new_password": "NewSecurePass456"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Схема запроса обновления access токена"""
    refresh_token: str = Field(..., description="Refresh токен")

    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }