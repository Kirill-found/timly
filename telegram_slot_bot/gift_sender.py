#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для отправки подарков со Stars победителям
"""
import asyncio
import logging
from typing import Dict, Optional
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

class GiftSender:
    """Отправка подарков со Stars"""

    # Маппинг желаемых сумм Stars на доступные gift_id
    # TODO: Заполнить реальными ID из каталога
    GIFT_MAPPING: Dict[int, str] = {
        15: None,    # Gift ID для 15 Stars
        25: None,    # Gift ID для 25 Stars
        50: None,    # Gift ID для 50 Stars
        100: None,   # Gift ID для 100 Stars
        200: None,   # Gift ID для 200 Stars (если есть)
        350: None,   # Gift ID для 350 Stars (если есть)
        500: None,   # Gift ID для 500 Stars (если есть)
    }

    def __init__(self, bot: Bot):
        self.bot = bot
        self._gifts_cache = None

    async def initialize(self):
        """Инициализация - получение каталога подарков"""
        try:
            logger.info("Получаю каталог доступных подарков...")
            gifts = await self.bot.get_available_gifts()

            self._gifts_cache = {}
            for gift in gifts.gifts:
                self._gifts_cache[gift.star_count] = gift.id
                logger.info(f"  ⭐ {gift.star_count} Stars → Gift ID: {gift.id}")

            # Обновляем маппинг
            for stars in self.GIFT_MAPPING.keys():
                if stars in self._gifts_cache:
                    self.GIFT_MAPPING[stars] = self._gifts_cache[stars]

            logger.info(f"✅ Загружено {len(self._gifts_cache)} подарков")

            # Показываем что доступно
            available = [k for k, v in self.GIFT_MAPPING.items() if v is not None]
            unavailable = [k for k, v in self.GIFT_MAPPING.items() if v is None]

            if available:
                logger.info(f"✅ Доступны подарки: {available} Stars")
            if unavailable:
                logger.warning(f"⚠️ НЕ ДОСТУПНЫ подарки: {unavailable} Stars")

            return True

        except Exception as e:
            logger.error(f"❌ Ошибка получения каталога подарков: {e}")
            return False

    async def send_gift(self, user_id: int, stars_amount: int, text: str = None) -> bool:
        """
        Отправить подарок пользователю

        Args:
            user_id: ID пользователя Telegram
            stars_amount: Сумма Stars для отправки (100, 200, 350, 500)
            text: Текст сообщения к подарку

        Returns:
            True если успешно, False если ошибка
        """
        try:
            # Проверяем есть ли подарок с такой суммой
            if stars_amount not in self.GIFT_MAPPING:
                logger.error(f"❌ Неизвестная сумма Stars: {stars_amount}")
                return False

            gift_id = self.GIFT_MAPPING[stars_amount]

            if gift_id is None:
                logger.warning(f"⚠️ Подарок на {stars_amount} Stars НЕ ДОСТУПЕН в каталоге!")
                # Пробуем отправить несколько подарков
                return await self._send_multiple_gifts(user_id, stars_amount, text)

            # Формируем текст
            if text is None:
                text = f"🎉 Поздравляем! Вы выиграли {stars_amount} ⭐ Stars!"

            # Отправляем подарок
            logger.info(f"📤 Отправка подарка {stars_amount} Stars пользователю {user_id}")

            result = await self.bot.send_gift(
                user_id=user_id,
                gift_id=gift_id,
                text=text
            )

            logger.info(f"✅ Подарок отправлен: {result}")
            return True

        except TelegramError as e:
            if "BALANCE_TOO_LOW" in str(e):
                logger.error(f"❌ Недостаточно Stars на балансе бота!")
                logger.error(f"   Нужно пополнить баланс через платные сообщения")
            else:
                logger.error(f"❌ Ошибка отправки подарка: {e}")
            return False

        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка: {e}")
            return False

    async def _send_multiple_gifts(self, user_id: int, total_stars: int, text: str) -> bool:
        """
        Отправить несколько подарков чтобы набрать нужную сумму

        Например: 200 Stars = 2 × 100 Stars
                  350 Stars = 3 × 100 + 1 × 50 Stars
                  500 Stars = 5 × 100 Stars
        """
        logger.info(f"🔄 Попытка отправить {total_stars} Stars через несколько подарков...")

        # Определяем комбинацию подарков
        combinations = {
            200: [(100, 2)],  # 2 подарка по 100
            350: [(100, 3), (50, 1)],  # 3×100 + 1×50
            500: [(100, 5)],  # 5 подарков по 100
        }

        if total_stars not in combinations:
            logger.error(f"❌ Нет комбинации для {total_stars} Stars")
            return False

        # Отправляем подарки
        combo = combinations[total_stars]
        gifts_sent = 0

        for stars, count in combo:
            gift_id = self.GIFT_MAPPING.get(stars)

            if gift_id is None:
                logger.error(f"❌ Подарок на {stars} Stars недоступен!")
                return False

            for i in range(count):
                try:
                    msg = f"{text}\n\nПодарок {gifts_sent + 1}/{sum(c for _, c in combo)}"

                    await self.bot.send_gift(
                        user_id=user_id,
                        gift_id=gift_id,
                        text=msg if i == 0 else None
                    )

                    gifts_sent += 1
                    logger.info(f"  ✅ Отправлен подарок {gifts_sent}: {stars} Stars")

                    # Небольшая задержка между подарками
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.error(f"  ❌ Ошибка отправки подарка #{gifts_sent + 1}: {e}")
                    return False

        logger.info(f"✅ Отправлено {gifts_sent} подарков на общую сумму {total_stars} Stars")
        return True

    async def check_balance(self) -> Optional[int]:
        """Проверить баланс Stars бота"""
        try:
            balance = await self.bot.get_star_transactions()
            # TODO: Реализовать подсчет баланса из транзакций
            logger.info(f"💰 Проверка баланса Stars бота...")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка проверки баланса: {e}")
            return None
