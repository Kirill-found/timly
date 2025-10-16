"""
Сервис для отправки уведомлений в Telegram
Уведомления о новых пользователях, платежах и событиях
"""
import logging
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError
import asyncio

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
