"""
Модель пользователя
"""
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class User(Base):
    """Модель пользователя системы"""
    __tablename__ = "users"
    
    # Первичный ключ
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Основные данные
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=True)
    
    # HH.ru интеграция
    encrypted_hh_token = Column(String, nullable=True)  # Зашифрованный токен
    token_verified = Column(Boolean, default=False)  # Проверен ли токен
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())