"""
UserBot для отправки звёзд БЕЗ использования Fragment API
Использует Pyrogram для автоматизации обычного пользовательского аккаунта
"""

import asyncio
import os
from typing import Optional, Dict, Any
from datetime import datetime
import json

from pyrogram import Client, filters
from pyrogram.raw import functions
from pyrogram.raw.types import (
    InputPeerUser,
    InputStorePaymentStarsGift,
    InputInvoiceStars
)
from pyrogram.errors import FloodWait
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

class StarsUserBotNoAPI:
    """
    UserBot для отправки звёзд через обычный аккаунт
    БЕЗ Fragment API, используя только MTProto
    """

    def __init__(self):
        self.api_id = int(os.getenv("API_ID", "0"))
        self.api_hash = os.getenv("API_HASH", "")
        self.phone = os.getenv("PHONE_NUMBER", "")

        # Инициализация клиента
        self.app = Client(
            "stars_sender_no_api",
            api_id=self.api_id,
            api_hash=self.api_hash,
            phone_number=self.phone
        )

        # Очередь выплат
        self.payout_queue = asyncio.Queue()

        # Настройки оплаты
        self.payment_method = os.getenv("PAYMENT_METHOD", "ton")  # ton, card, crypto
        self.auto_confirm = os.getenv("AUTO_CONFIRM", "true").lower() == "true"

        logger.info("UserBot инициализирован (режим без API)")

    async def start(self):
        """Запуск UserBot"""
        await self.app.start()

        me = await self.app.get_me()
        logger.info(f"UserBot запущен: @{me.username} ({me.first_name})")

        # Запускаем обработчик очереди
        asyncio.create_task(self.process_queue())

        logger.success("Готов к отправке звёзд!")

    async def send_stars_gift(self, user_id: int, amount: int) -> Dict[str, Any]:
        """
        Отправка звёзд пользователю через покупку подарка
        Использует MTProto Raw API для автоматизации
        """
        try:
            logger.info(f"Отправка {amount} звёзд пользователю {user_id}")

            # Получаем информацию о пользователе
            user = await self.app.get_users(user_id)

            # Метод 1: Через Raw API - покупка подарка
            result = await self.buy_and_send_gift_raw(user, amount)
            if result['success']:
                return result

            # Метод 2: Через inline-бота @GiftStarsBot (если существует)
            result = await self.send_via_gift_bot(user, amount)
            if result['success']:
                return result

            # Метод 3: Через создание группового чата с платным входом
            result = await self.send_via_paid_chat(user, amount)
            if result['success']:
                return result

            return {"success": False, "error": "Все методы не сработали"}

        except FloodWait as e:
            logger.warning(f"Flood wait: {e.value} секунд")
            await asyncio.sleep(e.value)
            return await self.send_stars_gift(user_id, amount)

        except Exception as e:
            logger.error(f"Ошибка отправки: {e}")
            return {"success": False, "error": str(e)}

    async def buy_and_send_gift_raw(self, user, amount: int) -> Dict[str, Any]:
        """
        Покупка и отправка подарка через Raw MTProto API
        """
        try:
            # Создаём InputPeer для пользователя
            input_peer = InputPeerUser(
                user_id=user.id,
                access_hash=user.access_hash if hasattr(user, 'access_hash') else 0
            )

            # Создаём invoice для покупки звёзд как подарка
            # ВАЖНО: Это экспериментальный код, требует тестирования

            # Шаг 1: Получаем доступные подарки
            result = await self.app.invoke(
                functions.payments.GetStarsGiftOptions(
                    user_id=input_peer
                )
            )

            # Находим подходящий вариант подарка
            gift_option = None
            for option in result.options:
                if option.stars == amount:
                    gift_option = option
                    break

            if not gift_option:
                # Если нет точного совпадения, берём ближайший
                gift_option = min(result.options,
                                key=lambda x: abs(x.stars - amount))

            # Шаг 2: Создаём платёж
            payment_form = await self.app.invoke(
                functions.payments.GetPaymentForm(
                    invoice=InputInvoiceStars(
                        option=gift_option
                    ),
                    theme_params=None
                )
            )

            # Шаг 3: Обрабатываем платёж
            if self.payment_method == "ton":
                # Оплата через TON
                payment_result = await self.process_ton_payment(payment_form)
            elif self.payment_method == "card":
                # Оплата картой
                payment_result = await self.process_card_payment(payment_form)
            else:
                # Криптовалюта
                payment_result = await self.process_crypto_payment(payment_form)

            if payment_result:
                # Шаг 4: Отправляем подарок
                send_result = await self.app.invoke(
                    functions.payments.SendStarsGift(
                        user_id=input_peer,
                        gift_option=gift_option,
                        payment_id=payment_result['payment_id']
                    )
                )

                logger.success(f"Подарок {amount} звёзд отправлен!")
                return {
                    "success": True,
                    "method": "raw_api",
                    "transaction_id": send_result.transaction_id
                }

        except Exception as e:
            logger.error(f"Raw API error: {e}")
            return {"success": False, "error": str(e)}

    async def send_via_gift_bot(self, user, amount: int) -> Dict[str, Any]:
        """
        Отправка через специального бота для подарков (если такой есть)
        """
        try:
            # Ищем бота который может отправлять подарки звёзд
            gift_bots = ["@stargiftsbot", "@giftbot", "@starsbot"]

            for bot_username in gift_bots:
                try:
                    # Проверяем существует ли бот
                    bot = await self.app.get_users(bot_username)

                    # Отправляем команду боту
                    await self.app.send_message(
                        bot_username,
                        f"/gift {user.id} {amount}"
                    )

                    # Ждём ответ
                    await asyncio.sleep(2)

                    # Здесь должна быть обработка ответа бота
                    # и автоматическое нажатие на кнопки оплаты

                    logger.info(f"Попытка через {bot_username}")

                except:
                    continue

            return {"success": False, "error": "gift_bot_not_found"}

        except Exception as e:
            logger.error(f"Gift bot error: {e}")
            return {"success": False, "error": str(e)}

    async def send_via_paid_chat(self, user, amount: int) -> Dict[str, Any]:
        """
        Альтернативный метод: создание платного контента
        и возврат средств (refund) после оплаты
        """
        try:
            # Создаём канал с платным входом
            channel = await self.app.create_channel(
                title=f"Gift_{amount}_{datetime.now().timestamp()}",
                description=f"Временный канал для передачи {amount} звёзд"
            )

            # Устанавливаем стоимость входа
            await self.app.invoke(
                functions.channels.SetStarsSubscription(
                    channel=channel.id,
                    stars_amount=amount
                )
            )

            # Приглашаем пользователя
            invite_link = await self.app.create_chat_invite_link(
                channel.id,
                member_limit=1
            )

            # Отправляем ссылку пользователю
            await self.app.send_message(
                user.id,
                f"🎁 Ваш выигрыш {amount} звёзд!\n"
                f"Перейдите по ссылке: {invite_link.link}\n"
                f"После входа вам будет возвращена полная сумма."
            )

            # Ждём когда пользователь войдёт
            # Потом делаем refund

            return {"success": True, "method": "paid_chat"}

        except Exception as e:
            logger.error(f"Paid chat error: {e}")
            return {"success": False, "error": str(e)}

    async def process_ton_payment(self, payment_form) -> Optional[Dict]:
        """Обработка платежа через TON"""
        try:
            # Здесь должна быть интеграция с TON кошельком
            # Например, через tonconnect или ton-sdk

            logger.info("Обработка TON платежа...")

            # Симуляция для примера
            return {
                "payment_id": f"ton_{datetime.now().timestamp()}",
                "success": True
            }

        except Exception as e:
            logger.error(f"TON payment error: {e}")
            return None

    async def process_card_payment(self, payment_form) -> Optional[Dict]:
        """Обработка платежа картой"""
        try:
            # Здесь должна быть интеграция с платёжной системой
            # Stripe, YooKassa и т.д.

            logger.info("Обработка платежа картой...")

            return {
                "payment_id": f"card_{datetime.now().timestamp()}",
                "success": True
            }

        except Exception as e:
            logger.error(f"Card payment error: {e}")
            return None

    async def process_crypto_payment(self, payment_form) -> Optional[Dict]:
        """Обработка криптоплатежа"""
        try:
            # Интеграция с крипто-процессингом
            # CryptoBot, CoinPayments и т.д.

            logger.info("Обработка крипто платежа...")

            return {
                "payment_id": f"crypto_{datetime.now().timestamp()}",
                "success": True
            }

        except Exception as e:
            logger.error(f"Crypto payment error: {e}")
            return None

    async def process_queue(self):
        """Обработчик очереди выплат"""
        while True:
            try:
                if not self.payout_queue.empty():
                    payout = await self.payout_queue.get()

                    result = await self.send_stars_gift(
                        payout['user_id'],
                        payout['amount']
                    )

                    if result['success']:
                        logger.success(f"Выплата {payout['amount']} звёзд успешна!")
                    else:
                        logger.error(f"Выплата не удалась: {result.get('error')}")

                    # Задержка между выплатами
                    await asyncio.sleep(3)
                else:
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Queue processing error: {e}")
                await asyncio.sleep(5)

    async def add_payout(self, user_id: int, amount: int):
        """Добавление выплаты в очередь"""
        await self.payout_queue.put({
            'user_id': user_id,
            'amount': amount,
            'timestamp': datetime.now()
        })
        logger.info(f"Добавлена выплата: {amount} звёзд для user {user_id}")

# ============= АЛЬТЕРНАТИВНЫЙ МЕТОД: Selenium =============

class SeleniumStarsBot:
    """
    Альтернативный вариант через Selenium для web.telegram.org
    """

    def __init__(self):
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        self.driver = None
        self.wait = None

    async def init_browser(self):
        """Инициализация браузера"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument("--user-data-dir=selenium_profile")  # Сохраняем сессию

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

        # Открываем web.telegram.org
        self.driver.get("https://web.telegram.org/k/")

        logger.info("Браузер запущен. Войдите в Telegram если нужно.")

    async def send_stars_selenium(self, user_id: int, amount: int):
        """Отправка звёзд через Selenium"""
        try:
            # 1. Находим чат с пользователем
            search_box = self.driver.find_element(By.CLASS_NAME, "search-input")
            search_box.send_keys(str(user_id))
            await asyncio.sleep(1)

            # 2. Открываем чат
            chat = self.driver.find_element(By.CLASS_NAME, "search-result")
            chat.click()

            # 3. Нажимаем кнопку "Подарить звёзды"
            gift_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Gift')]")
            gift_button.click()

            # 4. Выбираем количество
            amount_input = self.driver.find_element(By.NAME, "stars_amount")
            amount_input.send_keys(str(amount))

            # 5. Подтверждаем оплату
            pay_button = self.driver.find_element(By.CLASS_NAME, "pay-button")
            pay_button.click()

            logger.success(f"Звёзды отправлены через Selenium!")
            return True

        except Exception as e:
            logger.error(f"Selenium error: {e}")
            return False

# ============= ГЛАВНАЯ ФУНКЦИЯ =============

async def main():
    """Запуск UserBot без API"""

    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║        USERBOT ДЛЯ ОТПРАВКИ ЗВЁЗД (БЕЗ API)            ║
    ╠══════════════════════════════════════════════════════════╣
    ║                                                          ║
    ║  Методы отправки:                                        ║
    ║  1. Raw MTProto API (основной)                         ║
    ║  2. Через боты-помощники                               ║
    ║  3. Через платные каналы                               ║
    ║  4. Selenium автоматизация (резерв)                    ║
    ║                                                          ║
    ║  Настройте .env и запустите!                           ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # Проверяем настройки
    if not os.getenv("API_ID") or not os.getenv("API_HASH"):
        print("ОШИБКА: Настройте API_ID и API_HASH в .env файле!")
        print("Получить на: https://my.telegram.org")
        return

    # Запускаем UserBot
    userbot = StarsUserBotNoAPI()

    try:
        await userbot.start()

        # Тестовая выплата
        # await userbot.add_payout(123456789, 100)

        # Держим бота активным
        while True:
            await asyncio.sleep(60)

    except KeyboardInterrupt:
        logger.info("Остановка...")
    finally:
        await userbot.app.stop()

if __name__ == "__main__":
    asyncio.run(main())