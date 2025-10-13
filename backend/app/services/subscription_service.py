"""
Сервис управления подписками и тарификацией
Проверка лимитов, обновление подписок, логирование использования
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime, timedelta
import uuid
import json

from app.models.subscription import (
    Subscription, SubscriptionPlan, SubscriptionStatus,
    PlanType, UsageLog
)
from app.models.user import User
from app.utils.exceptions import ValidationError


class SubscriptionService:
    """Сервис для работы с подписками"""

    def __init__(self, db: Session):
        self.db = db

    async def get_or_create_subscription(self, user_id: uuid.UUID) -> Subscription:
        """
        Получить активную подписку пользователя или создать бесплатную
        """
        # Ищем активную подписку
        subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status.in_([SubscriptionStatus.active, SubscriptionStatus.trial])
        ).first()

        if subscription:
            # Проверяем необходимость сброса месячных лимитов
            if subscription.should_reset_monthly_usage():
                subscription.reset_monthly_usage()
                self.db.commit()

            # Проверяем не истекла ли подписка
            if subscription.expires_at and datetime.utcnow() > subscription.expires_at:
                subscription.status = SubscriptionStatus.expired
                self.db.commit()
                # Создаём новую бесплатную подписку
                return await self._create_free_subscription(user_id)

            return subscription

        # Создаём бесплатную подписку
        return await self._create_free_subscription(user_id)

    async def _create_free_subscription(self, user_id: uuid.UUID) -> Subscription:
        """Создание бесплатной подписки для пользователя"""
        # Получаем бесплатный план
        free_plan = self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.plan_type == PlanType.free
        ).first()

        if not free_plan:
            raise ValidationError("Бесплатный тарифный план не найден в системе")

        # Создаём подписку
        subscription = Subscription(
            user_id=user_id,
            plan_id=free_plan.id,
            status=SubscriptionStatus.active,
            started_at=datetime.utcnow(),
            expires_at=None  # Бесплатная подписка бессрочная
        )

        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)

        return subscription

    async def check_can_analyze(self, user_id: uuid.UUID) -> Tuple[bool, Optional[str]]:
        """
        Проверка возможности выполнения анализа
        Returns: (можно_ли, сообщение_об_ошибке)
        """
        subscription = await self.get_or_create_subscription(user_id)
        return subscription.can_analyze()

    async def check_can_export(self, user_id: uuid.UUID) -> Tuple[bool, Optional[str]]:
        """
        Проверка возможности экспорта
        Returns: (можно_ли, сообщение_об_ошибке)
        """
        subscription = await self.get_or_create_subscription(user_id)
        return subscription.can_export()

    async def check_vacancy_limit(self, user_id: uuid.UUID) -> Tuple[bool, Optional[str]]:
        """
        Проверка лимита активных вакансий
        Returns: (можно_ли, сообщение_об_ошибке)
        """
        from app.models.vacancy import Vacancy

        subscription = await self.get_or_create_subscription(user_id)

        # Считаем активные вакансии пользователя
        active_count = self.db.query(func.count(Vacancy.id)).filter(
            Vacancy.user_id == user_id,
            Vacancy.is_active == True
        ).scalar()

        if active_count >= subscription.plan.max_active_vacancies:
            return False, f"Достигнут лимит активных вакансий ({subscription.plan.max_active_vacancies})"

        return True, None

    async def increment_analysis_usage(
        self,
        user_id: uuid.UUID,
        application_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Увеличить счётчик использования анализов"""
        subscription = await self.get_or_create_subscription(user_id)

        subscription.analyses_used_this_month += 1
        self.db.commit()

        # Логируем использование
        await self._log_usage(
            user_id=user_id,
            subscription_id=subscription.id,
            action_type="analysis",
            application_id=application_id,
            metadata=metadata
        )

    async def increment_export_usage(
        self,
        user_id: uuid.UUID,
        vacancy_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Увеличить счётчик использования экспортов"""
        subscription = await self.get_or_create_subscription(user_id)

        subscription.exports_used_this_month += 1
        self.db.commit()

        # Логируем использование
        await self._log_usage(
            user_id=user_id,
            subscription_id=subscription.id,
            action_type="export",
            vacancy_id=vacancy_id,
            metadata=metadata
        )

    async def _log_usage(
        self,
        user_id: uuid.UUID,
        subscription_id: uuid.UUID,
        action_type: str,
        vacancy_id: Optional[uuid.UUID] = None,
        application_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Создать лог записи использования"""
        log_entry = UsageLog(
            user_id=user_id,
            subscription_id=subscription_id,
            action_type=action_type,
            vacancy_id=vacancy_id,
            application_id=application_id,
            action_metadata=json.dumps(metadata) if metadata else None
        )

        self.db.add(log_entry)
        self.db.commit()

    async def get_all_plans(self) -> List[SubscriptionPlan]:
        """Получить все активные тарифные планы"""
        return self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.is_active == True
        ).order_by(SubscriptionPlan.display_order).all()

    async def get_plan_by_type(self, plan_type: PlanType) -> Optional[SubscriptionPlan]:
        """Получить тарифный план по типу"""
        return self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.plan_type == plan_type,
            SubscriptionPlan.is_active == True
        ).first()

    async def upgrade_subscription(
        self,
        user_id: uuid.UUID,
        new_plan_type: PlanType,
        duration_months: int = 1
    ) -> Subscription:
        """
        Обновление тарифного плана пользователя

        Args:
            user_id: ID пользователя
            new_plan_type: Новый тип плана
            duration_months: Длительность в месяцах (1 или 12)
        """
        # Получаем новый план
        new_plan = await self.get_plan_by_type(new_plan_type)
        if not new_plan:
            raise ValidationError(f"Тарифный план {new_plan_type.value} не найден")

        # Получаем текущую подписку
        current_subscription = await self.get_or_create_subscription(user_id)

        # Проверяем, не пытается ли пользователь "понизить" тариф в середине периода
        # Можно добавить логику пропорционального расчёта

        # Деактивируем текущую подписку
        current_subscription.status = SubscriptionStatus.cancelled
        current_subscription.cancelled_at = datetime.utcnow()

        # Создаём новую подписку
        new_subscription = Subscription(
            user_id=user_id,
            plan_id=new_plan.id,
            status=SubscriptionStatus.active,
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=duration_months * 30)
        )

        self.db.add(new_subscription)
        self.db.commit()
        self.db.refresh(new_subscription)

        return new_subscription

    async def get_usage_statistics(
        self,
        user_id: uuid.UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Получить статистику использования за последние N дней
        """
        from_date = datetime.utcnow() - timedelta(days=days)

        # Получаем подписку
        subscription = await self.get_or_create_subscription(user_id)

        # Получаем логи
        logs = self.db.query(UsageLog).filter(
            UsageLog.user_id == user_id,
            UsageLog.created_at >= from_date
        ).all()

        # Группируем по типу действия
        stats_by_action = {}
        for log in logs:
            action_type = log.action_type
            if action_type not in stats_by_action:
                stats_by_action[action_type] = 0
            stats_by_action[action_type] += 1

        # Получаем данные по дням для графика
        daily_stats = self.db.query(
            func.date(UsageLog.created_at).label('date'),
            UsageLog.action_type,
            func.count(UsageLog.id).label('count')
        ).filter(
            UsageLog.user_id == user_id,
            UsageLog.created_at >= from_date
        ).group_by(
            func.date(UsageLog.created_at),
            UsageLog.action_type
        ).all()

        daily_data = {}
        for stat in daily_stats:
            date_str = stat.date.isoformat()
            if date_str not in daily_data:
                daily_data[date_str] = {}
            daily_data[date_str][stat.action_type] = stat.count

        return {
            "period_days": days,
            "subscription": subscription.to_dict(),
            "total_usage": stats_by_action,
            "daily_usage": daily_data
        }

    async def check_feature_access(
        self,
        user_id: uuid.UUID,
        feature_name: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Проверить доступ к конкретной функции

        Args:
            user_id: ID пользователя
            feature_name: Название функции (api_access, priority_support, etc.)

        Returns:
            (доступно_ли, сообщение_об_ошибке)
        """
        subscription = await self.get_or_create_subscription(user_id)

        if not subscription.is_active:
            return False, "Подписка неактивна"

        if not subscription.plan.has_feature(feature_name):
            return False, f"Функция {feature_name} недоступна в вашем тарифном плане"

        return True, None
