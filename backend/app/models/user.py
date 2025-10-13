"""
Модель пользователя (HR менеджера)
Содержит зашифрованный HH.ru токен и настройки
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base, GUID


class UserRole(enum.Enum):
    """Роли пользователей в системе"""
    user = "user"
    admin = "admin"


class User(Base):
    """
    Модель пользователя системы
    Хранит зашифрованные токены HH.ru и профильную информацию
    """
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    company_name = Column(String(255), nullable=True)

    # HH.ru интеграция - КРИТИЧНО: токен должен быть зашифрован!
    encrypted_hh_token = Column(Text, nullable=True)
    token_verified = Column(Boolean, default=False, index=True)
    token_verified_at = Column(DateTime, nullable=True)

    # Статус и метаданные
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships устанавливаются через backref в других моделях

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"

    @property
    def has_hh_token(self) -> bool:
        """Проверка наличия HH.ru токена"""
        return self.encrypted_hh_token is not None and self.token_verified

    def to_dict(self):
        """Сериализация для API (без чувствительных данных)"""
        return {
            "id": str(self.id),
            "email": self.email,
            "role": self.role.value,
            "company_name": self.company_name,
            "has_hh_token": self.has_hh_token,
            "token_verified": self.token_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }