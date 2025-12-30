"""
Модель для хранения кодов восстановления пароля
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
import uuid

from app.database import Base, GUID


class PasswordResetCode(Base):
    """
    Модель кода восстановления пароля
    Хранит временные коды для сброса пароля
    """
    __tablename__ = "password_reset_codes"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # 6-значный код
    code = Column(String(6), nullable=False, index=True)

    # Срок действия кода (15 минут)
    expires_at = Column(DateTime, nullable=False)

    # Использован ли код
    is_used = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<PasswordResetCode(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
