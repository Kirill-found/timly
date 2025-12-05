#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User-bot для отправки подарков через MTProto API
Это обходит ограничения Bot API и дает доступ к полному каталогу подарков
"""
import asyncio
import logging
from typing import Optional, Dict
from telethon import TelegramClient
from telethon.tl.functions.payments import (
    GetStarGiftsRequest,
    GetPaymentFormRequest,
    SendStarsFormRequest
)
from telethon.tl.types import (
    InputInvoiceStarGift,
    InputStorePaymentStarsGift
)

logger = logging.getLogger(__name__)

class UserBotGiftSender:
    """
    User-bot для отправки подарков со Stars
    Использует MTProto API для обхода ограничений Bot API
    """

    def __init__(self, api_id: int, api_hash: str, phone: str):
        """
        Args:
            api_id: API ID из my.telegram.org
            api_hash: API Hash из my.telegram.org
            phone: Номер телефона для user-bot (в формате +1234567890)
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone

        self.client = TelegramClient('userbot_session', api_id, api_hash)
        self._gifts_cache: Dict[int, int] = {}  # stars_count -> gift_id

    async def start(self):
        """Запустить user-bot"""
        logger.info("🚀 Запуск user-bot...")

        await self.client.start(phone=self.phone)

        me = await self.client.get_me()
        logger.info(f"✅ User-bot подключен: {me.first_name} (ID: {me.id})")
        logger.info(f"   Телефон: {self.phone}")

        # Загружаем каталог подарков
        await self.load_gift_catalog()

        return True

    async def stop(self):
        """Остановить user-bot"""
        logger.info("⏸ Остановка user-bot...")
        await self.client.disconnect()

    async def load_gift_catalog(self):
        """Загрузить ПОЛНЫЙ каталог подарков через MTProto"""
        try:
            logger.info("📦 Загружаю ПОЛНЫЙ каталог подарков через MTProto API...")

            # Получаем каталог через MTProto (не Bot API!)
            result = await self.client(GetStarGiftsRequest(hash=0))

            # Кешируем подарки
            self._gifts_cache.clear()

            for gift in result.gifts:
                self._gifts_cache[gift.stars] = gift.id
                logger.info(f"   ⭐ {gift.stars} Stars → Gift ID: {gift.id}")

            logger.info(f"✅ Загружено {len(self._gifts_cache)} подарков!")

            # Показываем что доступно для нашей игры
            needed = [100, 200, 350, 500]
            available = [s for s in needed if s in self._gifts_cache]
            missing = [s for s in needed if s not in self._gifts_cache]

            if available:
                logger.info(f"✅ ДОСТУПНЫ для игры: {available} Stars")
            if missing:
                logger.warning(f"⚠️ НЕ НАЙДЕНЫ: {missing} Stars")

            return True

        except Exception as e:
            logger.error(f"❌ Ошибка загрузки каталога: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def send_gift(
        self,
        user_id: int,
        stars_amount: int,
        message: str = None
    ) -> bool:
        """
        Отправить подарок пользователю через MTProto API

        Args:
            user_id: ID пользователя Telegram
            stars_amount: Количество Stars (100, 200, 350, 500)
            message: Текст сообщения к подарку

        Returns:
            True если успешно, False если ошибка
        """
        try:
            # Проверяем есть ли такой подарок в каталоге
            if stars_amount not in self._gifts_cache:
                logger.error(f"❌ Подарок на {stars_amount} Stars НЕ НАЙДЕН в каталоге!")
                logger.error(f"   Доступны: {list(self._gifts_cache.keys())}")
                return False

            gift_id = self._gifts_cache[stars_amount]

            logger.info(f"📤 Отправка подарка {stars_amount} Stars пользователю {user_id}")
            logger.info(f"   Gift ID: {gift_id}")

            # Получаем entity пользователя
            user = await self.client.get_entity(user_id)

            # Формируем сообщение
            if message is None:
                message = f"🎉 Поздравляем! Вы выиграли {stars_amount} ⭐ Stars!"

            # ВАЖНО: Отправка подарка через MTProto
            # Шаг 1: Получаем форму платежа
            invoice = InputInvoiceStarGift(
                user_id=user,
                gift_id=gift_id,
                message=message,
                hide_name=False,  # Показываем имя отправителя
                include_upgrade=False  # Не включаем апгрейд
            )

            payment_form = await self.client(GetPaymentFormRequest(
                invoice=invoice
            ))

            logger.info(f"   Форма платежа получена, цена: {payment_form.invoice.total_amount} Stars")

            # Шаг 2: Отправляем оплату (Stars списываются с баланса user-bot аккаунта)
            result = await self.client(SendStarsFormRequest(
                form_id=payment_form.form_id,
                invoice=invoice
            ))

            logger.info(f"✅ Подарок успешно отправлен!")
            logger.info(f"   Пользователь должен получить {stars_amount} Stars")

            return True

        except Exception as e:
            error_msg = str(e)

            if "BALANCE_TOO_LOW" in error_msg or "STARS_BALANCE_TOO_LOW" in error_msg:
                logger.error(f"❌ Недостаточно Stars на балансе user-bot аккаунта!")
                logger.error(f"   Нужно пополнить баланс: купить Stars для этого аккаунта")
            else:
                logger.error(f"❌ Ошибка отправки подарка: {e}")
                import traceback
                traceback.print_exc()

            return False

    async def get_balance(self) -> Optional[int]:
        """Получить баланс Stars user-bot аккаунта"""
        try:
            # TODO: Реализовать получение баланса
            logger.info("💰 Проверка баланса Stars...")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения баланса: {e}")
            return None


# Пример использования
async def test_userbot():
    """Тестовая функция"""

    # ВАЖНО: Замени на свои данные!
    API_ID = 28668805  # Твой API ID
    API_HASH = "5bd18c34314bf74adfd2066dcc21b2bb"  # Твой API Hash
    PHONE = "+79897546891"  # Твой номер телефона

    if False:  # Данные заполнены, пропускаем проверку
        print("⚠️ ВНИМАНИЕ!")
        print("Замени API_ID, API_HASH и PHONE в коде!")
        print("Получи на https://my.telegram.org/apps")
        return

    sender = UserBotGiftSender(API_ID, API_HASH, PHONE)

    try:
        # Запускаем
        await sender.start()

        # Пример: отправить подарок
        # await sender.send_gift(
        #     user_id=123456789,  # ID получателя
        #     stars_amount=200,
        #     message="🎰 Поздравляем с выигрышем!"
        # )

        print("\n✅ User-bot готов к работе!")
        print("Можно отправлять подарки через sender.send_gift()")

    finally:
        await sender.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(test_userbot())
