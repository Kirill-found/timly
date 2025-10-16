"""
Модели для системы платежей
Хранение информации о транзакциях и платежах через ЮKassa
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from datetime import datetime
from typing import Dict, Any

from app.database import Base, GUID


class PaymentStatus(enum.Enum):
    """Статусы платежа"""
    pending = "pending"  # Ожидает оплаты
    succeeded = "succeeded"  # Успешно оплачен
    canceled = "canceled"  # Отменен
    refunded = "refunded"  # Возвращен


class Payment(Base):
    """
    Платеж через ЮKassa
    Хранит информацию о транзакциях пользователей
    """
    __tablename__ = "payments"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(GUID, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True)

    # ЮKassa данные
    yookassa_payment_id = Column(String(255), unique=True, nullable=False, index=True)
    yookassa_status = Column(Enum(PaymentStatus), nullable=False, index=True)

    # Детали платежа
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="RUB")
    description = Column(Text, nullable=True)

    # Данные о тарифе
    plan_type = Column(String(50), nullable=False)  # Какой тариф оплачен
    duration_months = Column(Integer, nullable=False, default=1)  # На сколько месяцев

    # Метаданные (JSON)
    payment_method = Column(Text, nullable=True)  # Способ оплаты (карта, кошелек и т.д.)
    payment_metadata = Column(Text, nullable=True)  # Дополнительная информация (переименовано из metadata)

    # Временные метки
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    paid_at = Column(DateTime, nullable=True)  # Время успешной оплаты
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="payments")
    subscription = relationship("Subscription", backref="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.yookassa_status.value})>"

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация для API"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "yookassa_payment_id": self.yookassa_payment_id,
            "status": self.yookassa_status.value,
            "amount": self.amount,
            "currency": self.currency,
            "description": self.description,
            "plan_type": self.plan_type,
            "duration_months": self.duration_months,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
        }
