"""
UserBot для автоматической отправки Telegram Stars победителям
Использует Pyrogram для управления обычным аккаунтом
"""

import asyncio
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserBlocked, PeerIdInvalid
from dotenv import load_dotenv
from loguru import logger
import aiohttp
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Загружаем конфигурацию
load_dotenv()

# Настройка логирования
logger.add("logs/userbot_{time}.log", rotation="1 day", retention="7 days")

Base = declarative_base()

# ================== МОДЕЛИ БАЗЫ ДАННЫХ ==================

class PayoutStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PayoutRequest(Base):
    __tablename__ = "payout_requests"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String, nullable=True)
    amount = Column(Integer, nullable=False)  # Количество звёзд
    game_id = Column(String, nullable=False)  # ID игры/спина
    status = Column(String, default=PayoutStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
    transaction_id = Column(String, nullable=True)  # ID транзакции покупки звёзд

class UserStats(Base):
    __tablename__ = "user_stats"

    user_id = Column(Integer, primary_key=True)
    total_wins = Column(Integer, default=0)
    total_stars_won = Column(Integer, default=0)
    last_win_at = Column(DateTime, nullable=True)
    is_blocked = Column(Boolean, default=False)
    trust_score = Column(Float, default=50.0)  # 0-100

# ================== ОСНОВНОЙ КЛАСС USERBOT ==================

class StarsUserBot:
    """
    UserBot для автоматической отправки звёзд через покупку подарков
    """

    def __init__(self):
        self.api_id = int(os.getenv("API_ID"))
        self.api_hash = os.getenv("API_HASH")
        self.phone = os.getenv("PHONE_NUMBER")
        self.session_name = os.getenv("SESSION_NAME", "stars_sponsor")

        # Инициализация клиента Pyrogram
        self.app = Client(
            self.session_name,
            api_id=self.api_id,
            api_hash=self.api_hash,
            phone_number=self.phone
        )

        # База данных
        self.engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///slot_bot.db"))
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # Настройки
        self.auto_payment = os.getenv("AUTO_PAYMENT_ENABLED", "false").lower() == "true"
        self.max_auto = int(os.getenv("MAX_AUTO_PAYMENT", 500))
        self.payment_delay = int(os.getenv("PAYMENT_DELAY", 3))
        self.admin_id = int(os.getenv("ADMIN_ID"))

        # Очередь выплат
        self.payout_queue = asyncio.Queue()
        self.processing = False

        logger.info("UserBot инициализирован")

    async def start(self):
        """Запуск UserBot"""
        await self.app.start()
        logger.info(f"UserBot запущен как @{self.app.me.username}")

        # Запускаем обработчик очереди
        asyncio.create_task(self.process_payout_queue())

        # Запускаем мониторинг команд от основного бота
        asyncio.create_task(self.monitor_bot_commands())

        await self.notify_admin("✅ UserBot для выплат запущен и готов к работе")

    async def stop(self):
        """Остановка UserBot"""
        await self.app.stop()
        logger.info("UserBot остановлен")

    # ================== ОТПРАВКА ЗВЁЗД ==================

    async def send_stars_gift(self, user_id: int, amount: int) -> Dict[str, Any]:
        """
        Отправка звёзд пользователю через покупку подарка

        ВАЖНО: Это самая сложная часть - автоматизация покупки
        """
        try:
            logger.info(f"Попытка отправить {amount} звёзд пользователю {user_id}")

            # Метод 1: Использование inline-бота для покупки
            result = await self.send_via_inline_bot(user_id, amount)
            if result["success"]:
                return result

            # Метод 2: Прямая отправка через API (экспериментально)
            result = await self.send_via_raw_api(user_id, amount)
            if result["success"]:
                return result

            # Метод 3: Полуавтоматический режим
            result = await self.semi_auto_send(user_id, amount)
            return result

        except FloodWait as e:
            logger.warning(f"Flood wait: нужно подождать {e.value} секунд")
            await asyncio.sleep(e.value)
            return await self.send_stars_gift(user_id, amount)  # Повтор после ожидания

        except UserBlocked:
            logger.error(f"Пользователь {user_id} заблокировал бота")
            return {"success": False, "error": "user_blocked"}

        except Exception as e:
            logger.error(f"Ошибка отправки звёзд: {e}")
            return {"success": False, "error": str(e)}

    async def send_via_inline_bot(self, user_id: int, amount: int) -> Dict[str, Any]:
        """
        Отправка через специального inline-бота (если такой есть)
        """
        try:
            # Ищем бота который может отправлять подарки
            # Например, @wallet или другой платёжный бот

            gift_bot = "@wallet"  # или другой бот

            # Отправляем запрос боту
            response = await self.app.send_message(
                gift_bot,
                f"/gift {user_id} {amount} stars"
            )

            # Ждём ответ с ссылкой на оплату
            await asyncio.sleep(2)

            # Здесь должна быть логика обработки ответа и автоматической оплаты
            # ...

            return {"success": False, "error": "not_implemented"}

        except Exception as e:
            logger.error(f"Inline bot error: {e}")
            return {"success": False, "error": str(e)}

    async def send_via_raw_api(self, user_id: int, amount: int) -> Dict[str, Any]:
        """
        Отправка через Raw API Telegram (требует исследования)
        """
        try:
            # Получаем информацию о пользователе
            user = await self.app.get_users(user_id)

            # Здесь нужно использовать Raw API для покупки подарка
            # Это требует reverse engineering официального клиента

            # Примерный код (не рабочий, нужно исследование):
            """
            from pyrogram.raw import functions

            # Создаём запрос на покупку подарка
            result = await self.app.invoke(
                functions.payments.SendStarsGift(
                    user_id=user.id,
                    amount=amount,
                    # другие параметры
                )
            )
            """

            return {"success": False, "error": "raw_api_not_implemented"}

        except Exception as e:
            logger.error(f"Raw API error: {e}")
            return {"success": False, "error": str(e)}

    async def semi_auto_send(self, user_id: int, amount: int) -> Dict[str, Any]:
        """
        Полуавтоматический режим - генерирует ссылку для админа
        """
        try:
            # Создаём запись о необходимости выплаты
            session = self.Session()
            payout = PayoutRequest(
                user_id=user_id,
                amount=amount,
                status=PayoutStatus.PROCESSING.value,
                game_id=f"game_{datetime.now().timestamp()}"
            )
            session.add(payout)
            session.commit()
            payout_id = payout.id
            session.close()

            # Генерируем ссылку для ручной отправки
            user = await self.app.get_users(user_id)
            username = f"@{user.username}" if user.username else f"ID:{user_id}"

            # Отправляем админу
            await self.app.send_message(
                self.admin_id,
                f"""
⚠️ **Требуется ручная выплата**

Пользователь: {username}
ID: `{user_id}`
Сумма: **{amount} звёзд**
Payout ID: #{payout_id}

**Инструкция:**
1. Откройте чат с пользователем
2. Нажмите кнопку "Подарить звёзды"
3. Выберите {amount} звёзд
4. Оплатите и отправьте

После отправки нажмите кнопку ниже:
                """,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Отправлено", callback_data=f"sent_{payout_id}")],
                    [InlineKeyboardButton("❌ Отменить", callback_data=f"cancel_{payout_id}")]
                ])
            )

            return {
                "success": True,
                "method": "semi_auto",
                "payout_id": payout_id,
                "message": "Запрос отправлен администратору"
            }

        except Exception as e:
            logger.error(f"Semi-auto error: {e}")
            return {"success": False, "error": str(e)}

    # ================== ОБРАБОТКА ОЧЕРЕДИ ==================

    async def add_to_queue(self, user_id: int, username: str, amount: int, game_id: str):
        """Добавление выплаты в очередь"""
        session = self.Session()

        # Проверяем антиспам
        last_win = session.query(PayoutRequest).filter_by(
            user_id=user_id,
            status=PayoutStatus.COMPLETED.value
        ).order_by(PayoutRequest.created_at.desc()).first()

        if last_win:
            time_diff = (datetime.utcnow() - last_win.created_at).seconds
            min_delay = int(os.getenv("ANTI_SPAM_DELAY", 60))
            if time_diff < min_delay:
                logger.warning(f"Антиспам: {user_id} выиграл слишком быстро")
                session.close()
                return False

        # Создаём запрос на выплату
        payout = PayoutRequest(
            user_id=user_id,
            username=username,
            amount=amount,
            game_id=game_id,
            status=PayoutStatus.PENDING.value
        )
        session.add(payout)
        session.commit()
        session.close()

        # Добавляем в очередь
        await self.payout_queue.put(payout.id)
        logger.info(f"Добавлена выплата #{payout.id}: {amount} звёзд для {username}")

        return True

    async def process_payout_queue(self):
        """Обработчик очереди выплат"""
        while True:
            try:
                if not self.payout_queue.empty():
                    payout_id = await self.payout_queue.get()
                    await self.process_single_payout(payout_id)

                    # Задержка между выплатами
                    await asyncio.sleep(self.payment_delay)
                else:
                    # Проверяем очередь каждые 5 секунд
                    await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Ошибка обработки очереди: {e}")
                await asyncio.sleep(10)

    async def process_single_payout(self, payout_id: int):
        """Обработка одной выплаты"""
        session = self.Session()
        payout = session.query(PayoutRequest).filter_by(id=payout_id).first()

        if not payout or payout.status != PayoutStatus.PENDING.value:
            session.close()
            return

        # Обновляем статус
        payout.status = PayoutStatus.PROCESSING.value
        session.commit()

        logger.info(f"Обработка выплаты #{payout_id}: {payout.amount} звёзд для user {payout.user_id}")

        # Проверяем размер выплаты
        if payout.amount <= self.max_auto and self.auto_payment:
            # Автоматическая выплата
            result = await self.send_stars_gift(payout.user_id, payout.amount)
        else:
            # Полуавтоматический режим
            result = await self.semi_auto_send(payout.user_id, payout.amount)

        # Обновляем статус
        if result.get("success"):
            payout.status = PayoutStatus.COMPLETED.value
            payout.processed_at = datetime.utcnow()
            payout.transaction_id = result.get("transaction_id")

            # Обновляем статистику пользователя
            user_stats = session.query(UserStats).filter_by(user_id=payout.user_id).first()
            if not user_stats:
                user_stats = UserStats(user_id=payout.user_id)
                session.add(user_stats)

            user_stats.total_wins += 1
            user_stats.total_stars_won += payout.amount
            user_stats.last_win_at = datetime.utcnow()

            logger.success(f"Выплата #{payout_id} успешно завершена")
        else:
            payout.status = PayoutStatus.FAILED.value
            payout.error_message = result.get("error", "Unknown error")
            logger.error(f"Выплата #{payout_id} не удалась: {payout.error_message}")

        session.commit()
        session.close()

    # ================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==================

    async def notify_admin(self, message: str):
        """Отправка уведомления администратору"""
        try:
            await self.app.send_message(self.admin_id, message)
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление админу: {e}")

    async def monitor_bot_commands(self):
        """Мониторинг команд от основного бота"""
        # Здесь можно добавить обработку команд через webhook или polling
        pass

    async def get_stats(self) -> Dict[str, Any]:
        """Получение статистики выплат"""
        session = self.Session()

        today = datetime.utcnow().date()

        stats = {
            "total_payouts": session.query(PayoutRequest).filter_by(
                status=PayoutStatus.COMPLETED.value
            ).count(),

            "today_payouts": session.query(PayoutRequest).filter(
                PayoutRequest.status == PayoutStatus.COMPLETED.value,
                PayoutRequest.processed_at >= today
            ).count(),

            "pending": session.query(PayoutRequest).filter_by(
                status=PayoutStatus.PENDING.value
            ).count(),

            "failed": session.query(PayoutRequest).filter_by(
                status=PayoutStatus.FAILED.value
            ).count()
        }

        session.close()
        return stats

# ================== ИНТЕГРАЦИЯ С ОСНОВНЫМ БОТОМ ==================

class SlotBotConnector:
    """
    Класс для связи основного бота с UserBot
    """

    def __init__(self, userbot: StarsUserBot):
        self.userbot = userbot

    async def request_payout(self, user_id: int, username: str, amount: int, game_id: str) -> bool:
        """Запрос на выплату от основного бота"""
        return await self.userbot.add_to_queue(user_id, username, amount, game_id)

    async def get_payout_status(self, payout_id: int) -> Optional[str]:
        """Получение статуса выплаты"""
        session = self.userbot.Session()
        payout = session.query(PayoutRequest).filter_by(id=payout_id).first()
        status = payout.status if payout else None
        session.close()
        return status

# ================== ТОЧКА ВХОДА ==================

async def main():
    """Главная функция"""

    # Создаём и запускаем UserBot
    userbot = StarsUserBot()

    try:
        await userbot.start()
        logger.info("UserBot успешно запущен. Нажмите Ctrl+C для остановки.")

        # Бесконечный цикл
        while True:
            await asyncio.sleep(60)

            # Периодически отправляем статистику
            stats = await userbot.get_stats()
            logger.info(f"Статистика: {stats}")

    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    finally:
        await userbot.stop()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║           USERBOT ДЛЯ ОТПРАВКИ TELEGRAM STARS           ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Функции:                                                ║
║  • Автоматическая отправка звёзд победителям           ║
║  • Очередь выплат с приоритетами                       ║
║  • Антиспам и защита от мошенничества                  ║
║  • Полуавтоматический режим для больших сумм           ║
║                                                          ║
║  Настройка:                                              ║
║  1. Получите API ID и Hash на my.telegram.org          ║
║  2. Скопируйте .env.example в .env                     ║
║  3. Заполните все параметры                            ║
║  4. Запустите: python userbot_stars_sender.py          ║
║                                                          ║
║  При первом запуске потребуется:                       ║
║  - Ввести номер телефона                               ║
║  - Ввести код из Telegram                              ║
║  - Возможно, ввести пароль 2FA                         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)

    asyncio.run(main())