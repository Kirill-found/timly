#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер User-bot для отправки подарков победителям
Интегрируется с основным ботом
"""
import asyncio
import logging
from typing import Optional, Dict
from telethon import TelegramClient
from telethon.tl.functions.payments import GetStarGiftsRequest, GetPaymentFormRequest, SendStarsFormRequest
from telethon.tl.types import InputInvoiceStarGift

logger = logging.getLogger(__name__)

# Данные из авторизации
API_ID = 28668805
API_HASH = "5bd18c34314bf74adfd2066dcc21b2bb"
PHONE = "+79897546891"

# Маппинг подарков для игры (ID из каталога)
GIFT_IDS = {
    100: 5170521118301225164,   # 100 Stars
    200: 6014591077976114307,   # 200 Stars
    350: 5933531623327795414,   # 350 Stars
    500: 6012607142387778152,   # 500 Stars
}

class UserBotManager:
    """
    Менеджер для управления user-bot и отправки подарков
    """

    def __init__(self):
        self.client = None
        self.is_running = False
        self._gifts_cache = GIFT_IDS.copy()

    async def start(self):
        """Запуск user-bot"""
        if self.is_running:
            logger.warning("User-bot уже запущен!")
            return

        try:
            logger.info("🚀 Запуск user-bot...")

            # Создаем клиент с существующей сессией
            self.client = TelegramClient('userbot_session', API_ID, API_HASH)
            await self.client.connect()

            if not await self.client.is_user_authorized():
                logger.error("❌ User-bot не авторизован! Запусти quick_auth.py")
                return False

            me = await self.client.get_me()
            logger.info(f"✅ User-bot подключен: {me.first_name} (ID: {me.id})")

            # Обновляем кеш подарков
            await self._update_gifts_cache()

            self.is_running = True
            logger.info("✅ User-bot готов к отправке подарков!")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка запуска user-bot: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def stop(self):
        """Остановка user-bot"""
        if not self.is_running:
            return

        logger.info("⏸ Остановка user-bot...")

        if self.client:
            await self.client.disconnect()

        self.is_running = False
        logger.info("✅ User-bot остановлен")

    async def _update_gifts_cache(self):
        """Обновление кеша подарков из каталога"""
        try:
            result = await self.client(GetStarGiftsRequest(hash=0))

            # Сохраняем ВСЕ подарки для каждой суммы (не только первый!)
            gifts_by_stars = {}
            for gift in result.gifts:
                stars = gift.stars
                if stars in [25, 50, 100]:
                    if stars not in gifts_by_stars:
                        gifts_by_stars[stars] = []

                    # Сохраняем подарок с информацией о доступности
                    gift_info = {
                        'id': gift.id,
                        'availability': getattr(gift, 'availability_remains', None),
                        'limited': getattr(gift, 'limited', False)
                    }
                    gifts_by_stars[stars].append(gift_info)

            # Теперь сохраняем в кеш списки подарков
            self._gifts_cache = gifts_by_stars

            # Логируем что нашли
            for stars, gifts_list in gifts_by_stars.items():
                available_count = sum(1 for g in gifts_list if g['availability'] is None or g['availability'] > 0)
                logger.info(f"  📦 {stars} Stars -> {len(gifts_list)} gifts ({available_count} available)")

        except Exception as e:
            logger.warning(f"⚠️ Не удалось обновить каталог: {e}")
            logger.info("Используем предустановленные ID подарков")

    async def send_gift(
        self,
        user_id: int,
        stars_amount: int,
        message: str = None
    ) -> bool:
        """
        Отправить подарок пользователю

        Args:
            user_id: ID пользователя Telegram
            stars_amount: Количество Stars (100, 200, 350, 500)
            message: Текст сообщения к подарку

        Returns:
            True если успешно, False если ошибка
        """
        if not self.is_running:
            logger.error("❌ User-bot не запущен!")
            return False

        if stars_amount not in self._gifts_cache:
            logger.error(f"❌ Подарок на {stars_amount} Stars не найден!")
            return False

        # Выбираем доступный подарок из списка
        gifts_list = self._gifts_cache[stars_amount]
        available_gift = None

        for gift_info in gifts_list:
            # Проверяем доступность (None = unlimited, >0 = available)
            if gift_info['availability'] is None or gift_info['availability'] > 0:
                available_gift = gift_info
                break

        if available_gift is None:
            logger.error(f"❌ Нет доступных подарков на {stars_amount} Stars!")
            logger.error(f"   Все {len(gifts_list)} подарков недоступны (USAGE_LIMITED)")
            return False

        try:
            gift_id = available_gift['id']

            logger.info(f"📤 Отправка подарка {stars_amount} Stars пользователю {user_id}")
            logger.info(f"   Gift ID: {gift_id}")
            if available_gift['availability'] is not None:
                logger.info(f"   Availability: {available_gift['availability']} remaining")

            # Получаем entity пользователя - пробуем разные способы
            try:
                # Способ 1: напрямую по ID (работает если есть в кэше)
                user_entity = await self.client.get_entity(user_id)
            except ValueError:
                # Способ 2: получаем через InputPeerUser напрямую
                logger.info(f"   Пытаюсь получить entity через InputPeerUser...")
                from telethon.tl.types import InputPeerUser
                # Получаем access hash (нужен для InputPeerUser)
                # Так как у нас нет access_hash, используем PeerUser напрямую
                from telethon.tl.types import PeerUser
                user_entity = PeerUser(user_id=user_id)

            # Создаем InputPeer
            from telethon.tl.types import InputPeerUser
            try:
                input_peer = await self.client.get_input_entity(user_entity)
            except:
                # Если не можем получить через get_input_entity, создаем вручную
                # ВАЖНО: для этого нужен access_hash, который мы не знаем
                # Попробуем получить пользователя из общих групп
                logger.info(f"   Ищу пользователя в общих чатах...")

                # Получаем все чаты user-bot
                async for dialog in self.client.iter_dialogs():
                    if dialog.is_group or dialog.is_channel:
                        try:
                            # Ищем пользователя в участниках группы
                            async for participant in self.client.iter_participants(dialog):
                                if participant.id == user_id:
                                    user_entity = participant
                                    input_peer = await self.client.get_input_entity(participant)
                                    logger.info(f"   Найден в группе: {dialog.name}")
                                    break
                            if hasattr(user_entity, 'first_name'):
                                break
                        except:
                            continue

                if not hasattr(user_entity, 'first_name'):
                    raise ValueError(f"Не могу найти пользователя {user_id}. User-bot должен быть в общей группе с пользователем!")

            logger.info(f"   Пользователь: {getattr(user_entity, 'first_name', 'Unknown')}")

            # ВАЖНО: Отправляем приветственное сообщение ПЕРЕД подарком
            # Это помогает избежать STARGIFT_USAGE_LIMITED - Telegram видит что есть диалог
            logger.info(f"   📨 Отправляю приветственное сообщение...")
            greeting_text = (
                f"🎰 Поздравляем с выигрышем!\n\n"
                f"Вы выиграли {stars_amount} ⭐ Stars в нашей слот-машине!\n"
                f"Сейчас отправлю вам подарок... 🎁"
            )

            try:
                await self.client.send_message(
                    entity=input_peer,
                    message=greeting_text
                )
                logger.info(f"   ✅ Приветственное сообщение отправлено")

                # Небольшая пауза чтобы Telegram зарегистрировал диалог
                import asyncio
                await asyncio.sleep(2)

            except Exception as msg_error:
                logger.warning(f"   ⚠️ Не удалось отправить сообщение: {msg_error}")
                # Продолжаем даже если сообщение не отправилось

            # Формируем сообщение
            if message is None:
                message = f"🎉 Поздравляем! Вы выиграли {stars_amount} ⭐ Stars!"

            # Создаем инвойс для подарка
            invoice = InputInvoiceStarGift(
                peer=input_peer,
                gift_id=gift_id,
                hide_name=False,  # Показываем имя отправителя
                include_upgrade=False,
                message=None  # Текст сообщения (пока None)
            )

            # Получаем форму платежа
            payment_form = await self.client(GetPaymentFormRequest(invoice=invoice))
            logger.info(f"   Форма платежа получена (form_id: {payment_form.form_id})")

            # Отправляем оплату (Stars списываются с баланса)
            result = await self.client(SendStarsFormRequest(
                form_id=payment_form.form_id,
                invoice=invoice
            ))

            logger.info(f"   Результат: {result}")

            logger.info(f"✅ Подарок {stars_amount} Stars успешно отправлен!")
            logger.info(f"   Пользователь получит уведомление")
            return True

        except Exception as e:
            error_msg = str(e)

            if "BALANCE_TOO_LOW" in error_msg or "STARS_BALANCE_TOO_LOW" in error_msg:
                logger.error(f"❌ Недостаточно Stars на балансе user-bot!")
                logger.error(f"   Нужно пополнить Stars для аккаунта {PHONE}")
            elif "USER_NOT_FOUND" in error_msg:
                logger.error(f"❌ Пользователь {user_id} не найден!")
            else:
                logger.error(f"❌ Ошибка отправки подарка: {e}")
                import traceback
                traceback.print_exc()

            return False

    async def get_balance(self) -> Optional[int]:
        """
        Получить баланс Stars (если доступно)
        """
        try:
            # TODO: Реализовать получение баланса через MTProto
            logger.info("💰 Проверка баланса Stars...")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения баланса: {e}")
            return None


# Глобальный экземпляр менеджера
_manager = None

async def get_userbot_manager() -> UserBotManager:
    """Получить глобальный экземпляр менеджера"""
    global _manager

    if _manager is None:
        _manager = UserBotManager()
        await _manager.start()

    return _manager


# Пример использования
async def test_send_gift():
    """Тест отправки подарка"""
    manager = await get_userbot_manager()

    # Отправляем тестовый подарок админу
    TEST_USER_ID = 6692743003  # Твой ID

    print()
    print("=" * 70)
    print("ТЕСТ ОТПРАВКИ ПОДАРКА")
    print("=" * 70)
    print()

    # Отправляем 100 Stars
    success = await manager.send_gift(
        user_id=TEST_USER_ID,
        stars_amount=100,
        message="🎰 Тестовый подарок от слот-бота!"
    )

    if success:
        print()
        print("✅ ТЕСТ УСПЕШЕН!")
        print("Проверь свой Telegram - должен прийти подарок 100 Stars!")
    else:
        print()
        print("❌ ТЕСТ ПРОВАЛЕН!")
        print("Проверь логи выше")

    await manager.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(test_send_gift())
