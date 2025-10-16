"""
Сервис для отправки уведомлений в Telegram
Уведомления о новых пользователях, платежах и событиях
"""
import logging
from typing import Optional, Dict, Any
from telegram import Bot
from telegram.error import TelegramError
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TelegramService:
    """Сервис для отправки уведомлений в Telegram"""

    def __init__(self):
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        self.admin_chat_id = getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', '')

        if self.bot_token and self.admin_chat_id:
            self.bot = Bot(token=self.bot_token)
            self.enabled = True
            logger.info("Telegram service initialized successfully")
        else:
            self.bot = None
            self.enabled = False
            logger.warning("Telegram service disabled - credentials not found")

    async def send_message(self, message: str, chat_id: Optional[str] = None) -> bool:
        """
        Отправить сообщение в Telegram

        Args:
            message: Текст сообщения
            chat_id: ID чата (по умолчанию - админский)

        Returns:
            True если отправка успешна
        """
        if not self.enabled:
            logger.debug("Telegram disabled, skipping message")
            return False

        try:
            target_chat_id = chat_id or self.admin_chat_id
            await self.bot.send_message(
                chat_id=target_chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"Telegram message sent to {target_chat_id}")
            return True

        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")
            return False

    async def notify_new_user(self, user_email: str, user_name: Optional[str] = None):
        """
        Уведомление о новом пользователе

        Args:
            user_email: Email пользователя
            user_name: Имя пользователя (опционально)
        """
        name = user_name or "Не указано"
        message = (
            f"🆕 <b>Новый пользователь зарегистрирован!</b>\n\n"
            f"👤 Имя: {name}\n"
            f"📧 Email: {user_email}\n"
            f"🕐 Время: {self._get_moscow_time()}"
        )
        await self.send_message(message)

    async def notify_new_payment(
        self,
        user_email: str,
        amount: float,
        plan_type: str,
        duration_months: int
    ):
        """
        Уведомление о новом платеже

        Args:
            user_email: Email пользователя
            amount: Сумма платежа
            plan_type: Тип тарифа
            duration_months: Длительность подписки
        """
        message = (
            f"💰 <b>Новый платеж!</b>\n\n"
            f"👤 Пользователь: {user_email}\n"
            f"💵 Сумма: {amount} ₽\n"
            f"📦 Тариф: {plan_type}\n"
            f"📅 Период: {duration_months} мес.\n"
            f"🕐 Время: {self._get_moscow_time()}"
        )
        await self.send_message(message)

    async def notify_subscription_expired(self, user_email: str, plan_type: str):
        """
        Уведомление об истечении подписки

        Args:
            user_email: Email пользователя
            plan_type: Тип тарифа
        """
        message = (
            f"⏰ <b>Подписка истекла</b>\n\n"
            f"👤 Пользователь: {user_email}\n"
            f"📦 Тариф: {plan_type}\n"
            f"🕐 Время: {self._get_moscow_time()}"
        )
        await self.send_message(message)

    async def notify_error(self, error_message: str, context: Optional[str] = None):
        """
        Уведомление об ошибке

        Args:
            error_message: Текст ошибки
            context: Контекст ошибки (опционально)
        """
        message = f"❌ <b>Ошибка в системе</b>\n\n"

        if context:
            message += f"📍 Контекст: {context}\n"

        message += (
            f"⚠️ Ошибка: {error_message}\n"
            f"🕐 Время: {self._get_moscow_time()}"
        )
        await self.send_message(message)

    async def send_statistics(self, db: Session):
        """
        Отправить статистику по пользователям и подпискам

        Args:
            db: Сессия базы данных
        """
        from app.models.user import User
        from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus, PlanType
        from app.models.payment import Payment, PaymentStatus

        try:
            # Общая статистика пользователей
            total_users = db.query(func.count(User.id)).scalar() or 0
            active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
            users_with_hh_token = db.query(func.count(User.id)).filter(
                User.token_verified == True
            ).scalar() or 0

            # Статистика по подпискам
            subscription_stats = db.query(
                SubscriptionPlan.plan_type,
                func.count(Subscription.id).label('count')
            ).join(
                Subscription, Subscription.plan_id == SubscriptionPlan.id
            ).filter(
                Subscription.status == SubscriptionStatus.active
            ).group_by(SubscriptionPlan.plan_type).all()

            # Словарь для подсчёта по тарифам
            plan_counts = {
                PlanType.free.value: 0,
                PlanType.starter.value: 0,
                PlanType.professional.value: 0,
                PlanType.enterprise.value: 0
            }

            for plan_type, count in subscription_stats:
                plan_counts[plan_type.value] = count

            # Пользователи без активной подписки
            users_without_subscription = total_users - sum(plan_counts.values())

            # Статистика платежей за последний месяц
            month_ago = datetime.utcnow() - timedelta(days=30)
            payments_last_month = db.query(func.count(Payment.id)).filter(
                and_(
                    Payment.created_at >= month_ago,
                    Payment.yookassa_status == PaymentStatus.succeeded
                )
            ).scalar() or 0

            revenue_last_month = db.query(func.sum(Payment.amount)).filter(
                and_(
                    Payment.created_at >= month_ago,
                    Payment.yookassa_status == PaymentStatus.succeeded
                )
            ).scalar() or 0.0

            # Новые пользователи за последнюю неделю
            week_ago = datetime.utcnow() - timedelta(days=7)
            new_users_week = db.query(func.count(User.id)).filter(
                User.created_at >= week_ago
            ).scalar() or 0

            # Формирование сообщения
            message = (
                f"📊 <b>Статистика платформы Timly</b>\n"
                f"🕐 {self._get_moscow_time()}\n\n"

                f"👥 <b>Пользователи</b>\n"
                f"├ Всего: {total_users}\n"
                f"├ Активных: {active_users}\n"
                f"├ С HH токеном: {users_with_hh_token}\n"
                f"└ Новых за неделю: {new_users_week}\n\n"

                f"💼 <b>Подписки (активные)</b>\n"
                f"├ 🆓 Free: {plan_counts['free']}\n"
                f"├ 🌱 Starter: {plan_counts['starter']}\n"
                f"├ 💎 Professional: {plan_counts['professional']}\n"
                f"├ 🏢 Enterprise: {plan_counts['enterprise']}\n"
                f"└ Без подписки: {users_without_subscription}\n\n"

                f"💰 <b>Платежи (30 дней)</b>\n"
                f"├ Транзакций: {payments_last_month}\n"
                f"└ Выручка: {revenue_last_month:,.2f} ₽"
            )

            await self.send_message(message)
            logger.info("Statistics sent to Telegram successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to send statistics: {e}")
            return False

    def _get_moscow_time(self) -> str:
        """Получить текущее время в московском формате"""
        from datetime import datetime, timezone, timedelta
        moscow_tz = timezone(timedelta(hours=3))
        now = datetime.now(moscow_tz)
        return now.strftime("%d.%m.%Y %H:%M:%S (МСК)")


# Singleton instance
_telegram_service = None


def get_telegram_service() -> TelegramService:
    """Получить экземпляр TelegramService (singleton)"""
    global _telegram_service
    if _telegram_service is None:
        _telegram_service = TelegramService()
    return _telegram_service


# Вспомогательные функции для удобного использования
async def notify_new_user(user_email: str, user_name: Optional[str] = None):
    """Отправить уведомление о новом пользователе"""
    service = get_telegram_service()
    await service.notify_new_user(user_email, user_name)


async def notify_new_payment(user_email: str, amount: float, plan_type: str, duration_months: int):
    """Отправить уведомление о новом платеже"""
    service = get_telegram_service()
    await service.notify_new_payment(user_email, amount, plan_type, duration_months)


async def notify_subscription_expired(user_email: str, plan_type: str):
    """Отправить уведомление об истечении подписки"""
    service = get_telegram_service()
    await service.notify_subscription_expired(user_email, plan_type)


async def notify_error(error_message: str, context: Optional[str] = None):
    """Отправить уведомление об ошибке"""
    service = get_telegram_service()
    await service.notify_error(error_message, context)
