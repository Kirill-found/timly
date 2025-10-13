"""
Модели для системы тарификации и подписок
Управление лимитами пользователей и тарифными планами
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from app.database import Base, GUID


class SubscriptionStatus(enum.Enum):
    """Статусы подписки"""
    active = "active"  # Активная подписка
    expired = "expired"  # Истекла
    cancelled = "cancelled"  # Отменена пользователем
    trial = "trial"  # Пробный период


class PlanType(enum.Enum):
    """Типы тарифных планов"""
    free = "free"
    starter = "starter"
    professional = "professional"
    enterprise = "enterprise"


class SubscriptionPlan(Base):
    """
    Тарифный план
    Определяет лимиты и возможности для пользователей
    """
    __tablename__ = "subscription_plans"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    plan_type = Column(Enum(PlanType), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Цены
    price_monthly = Column(Float, nullable=False, default=0.0)
    price_yearly = Column(Float, nullable=False, default=0.0)
    currency = Column(String(3), nullable=False, default="RUB")

    # Лимиты
    max_active_vacancies = Column(Integer, nullable=False, default=1)
    max_analyses_per_month = Column(Integer, nullable=False, default=50)
    max_export_per_month = Column(Integer, nullable=False, default=10)

    # Дополнительные возможности (JSON)
    # Пример: {"api_access": true, "priority_support": true, "custom_reports": true}
    features = Column(Text, nullable=True)

    # Метаданные
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")

    def __repr__(self):
        return f"<SubscriptionPlan(plan_type={self.plan_type.value}, name={self.name})>"

    @property
    def features_dict(self) -> Dict[str, Any]:
        """Парсинг JSON features в словарь"""
        if not self.features:
            return {}
        try:
            return json.loads(self.features)
        except json.JSONDecodeError:
            return {}

    def has_feature(self, feature_name: str) -> bool:
        """Проверка наличия функции в тарифе"""
        return self.features_dict.get(feature_name, False)

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация для API"""
        return {
            "id": str(self.id),
            "plan_type": self.plan_type.value,
            "name": self.name,
            "description": self.description,
            "pricing": {
                "monthly": self.price_monthly,
                "yearly": self.price_yearly,
                "currency": self.currency,
                "yearly_discount": round((1 - (self.price_yearly / (self.price_monthly * 12))) * 100, 1) if self.price_monthly > 0 else 0
            },
            "limits": {
                "active_vacancies": self.max_active_vacancies,
                "analyses_per_month": self.max_analyses_per_month,
                "exports_per_month": self.max_export_per_month
            },
            "features": self.features_dict,
            "display_order": self.display_order
        }


class Subscription(Base):
    """
    Подписка пользователя
    Связывает пользователя с тарифным планом и отслеживает использование
    """
    __tablename__ = "subscriptions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(GUID, ForeignKey("subscription_plans.id"), nullable=False, index=True)

    # Статус подписки
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.trial, nullable=False, index=True)

    # Период действия
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Отслеживание использования за текущий месяц
    analyses_used_this_month = Column(Integer, nullable=False, default=0)
    exports_used_this_month = Column(Integer, nullable=False, default=0)
    last_reset_at = Column(DateTime, nullable=False, server_default=func.now())

    # Метаданные
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription(user_id={self.user_id}, plan={self.plan.name if self.plan else 'None'}, status={self.status.value})>"

    @property
    def is_active(self) -> bool:
        """Проверка активности подписки"""
        if self.status in [SubscriptionStatus.cancelled, SubscriptionStatus.expired]:
            return False

        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False

        return True

    @property
    def days_remaining(self) -> Optional[int]:
        """Количество дней до окончания подписки"""
        if not self.expires_at:
            return None

        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)

    @property
    def usage_percentage(self) -> Dict[str, float]:
        """Процент использования лимитов"""
        if not self.plan:
            return {"analyses": 0.0, "exports": 0.0}

        analyses_pct = (self.analyses_used_this_month / self.plan.max_analyses_per_month * 100) if self.plan.max_analyses_per_month > 0 else 0
        exports_pct = (self.exports_used_this_month / self.plan.max_export_per_month * 100) if self.plan.max_export_per_month > 0 else 0

        return {
            "analyses": round(min(100, analyses_pct), 1),
            "exports": round(min(100, exports_pct), 1)
        }

    def should_reset_monthly_usage(self) -> bool:
        """Проверка необходимости сброса месячных счётчиков"""
        if not self.last_reset_at:
            return True

        # Сбрасываем если прошёл месяц с последнего сброса
        delta = datetime.utcnow() - self.last_reset_at
        return delta.days >= 30

    def reset_monthly_usage(self):
        """Сброс месячных счётчиков использования"""
        self.analyses_used_this_month = 0
        self.exports_used_this_month = 0
        self.last_reset_at = datetime.utcnow()

    def can_analyze(self) -> tuple[bool, Optional[str]]:
        """Проверка возможности выполнения анализа"""
        if not self.is_active:
            return False, "Подписка неактивна"

        if self.should_reset_monthly_usage():
            self.reset_monthly_usage()

        if self.analyses_used_this_month >= self.plan.max_analyses_per_month:
            return False, f"Достигнут лимит анализов ({self.plan.max_analyses_per_month} в месяц)"

        return True, None

    def can_export(self) -> tuple[bool, Optional[str]]:
        """Проверка возможности экспорта"""
        if not self.is_active:
            return False, "Подписка неактивна"

        if self.should_reset_monthly_usage():
            self.reset_monthly_usage()

        if self.exports_used_this_month >= self.plan.max_export_per_month:
            return False, f"Достигнут лимит экспортов ({self.plan.max_export_per_month} в месяц)"

        return True, None

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация для API"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "plan": self.plan.to_dict() if self.plan else None,
            "status": self.status.value,
            "is_active": self.is_active,
            "period": {
                "started_at": self.started_at.isoformat() if self.started_at else None,
                "expires_at": self.expires_at.isoformat() if self.expires_at else None,
                "days_remaining": self.days_remaining
            },
            "usage": {
                "analyses": {
                    "used": self.analyses_used_this_month,
                    "limit": self.plan.max_analyses_per_month if self.plan else 0,
                    "percentage": self.usage_percentage["analyses"]
                },
                "exports": {
                    "used": self.exports_used_this_month,
                    "limit": self.plan.max_export_per_month if self.plan else 0,
                    "percentage": self.usage_percentage["exports"]
                },
                "last_reset": self.last_reset_at.isoformat() if self.last_reset_at else None
            }
        }


class UsageLog(Base):
    """
    Лог использования ресурсов
    Для аналитики и аудита действий пользователей
    """
    __tablename__ = "usage_logs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(GUID, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True)

    # Тип действия
    action_type = Column(String(50), nullable=False, index=True)  # analysis, export, sync

    # Связанные ресурсы
    vacancy_id = Column(GUID, ForeignKey("vacancies.id", ondelete="SET NULL"), nullable=True)
    application_id = Column(GUID, ForeignKey("applications.id", ondelete="SET NULL"), nullable=True)

    # Метаданные действия (JSON)
    action_metadata = Column(Text, nullable=True)

    # Временная метка
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", backref="usage_logs")
    subscription = relationship("Subscription", backref="usage_logs")

    def __repr__(self):
        return f"<UsageLog(user_id={self.user_id}, action={self.action_type}, created_at={self.created_at})>"

    @property
    def metadata_dict(self) -> Dict[str, Any]:
        """Парсинг JSON action_metadata"""
        if not self.action_metadata:
            return {}
        try:
            return json.loads(self.action_metadata)
        except json.JSONDecodeError:
            return {}

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация для API"""
        return {
            "id": str(self.id),
            "action_type": self.action_type,
            "vacancy_id": str(self.vacancy_id) if self.vacancy_id else None,
            "application_id": str(self.application_id) if self.application_id else None,
            "metadata": self.metadata_dict,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
