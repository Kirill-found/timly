"""
Простая система выплат звёзд через UserBot
"""

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Настройки
ADMIN_ID = int(os.getenv('ADMIN_ID', '517682186'))
API_ID = int(os.getenv('API_ID', '28668805'))
API_HASH = os.getenv('API_HASH', '5bd18c34314bf74adfd2066dcc21b2bb')

class SimplePayoutSystem:
    """Простая система уведомлений о выплатах"""

    def __init__(self):
        self.app = Client(
            "stars_userbot",
            api_id=API_ID,
            api_hash=API_HASH
        )
        self.pending_payouts = []

    async def start(self):
        """Запуск UserBot"""
        print("\n" + "="*60)
        print("    ЗАПУСК СИСТЕМЫ УВЕДОМЛЕНИЙ О ВЫПЛАТАХ")
        print("="*60 + "\n")

        await self.app.start()
        me = await self.app.get_me()

        print(f"[OK] UserBot запущен")
        print(f"Аккаунт: {me.first_name} (@{me.username or 'NoUsername'})")
        print(f"ID: {me.id}")
        print(f"Телефон: {me.phone_number}\n")

        # Отправляем тестовое сообщение
        await self.send_test_notification()

        print("="*60)
        print("    СИСТЕМА ГОТОВА!")
        print("="*60 + "\n")
        print("Для теста выплаты используйте:")
        print("  python test_payout.py <user_id> <amount>\n")

        # Держим соединение
        await asyncio.Event().wait()

    async def send_test_notification(self):
        """Отправка тестового уведомления"""
        try:
            await self.app.send_message(
                ADMIN_ID,
                f"✅ **Система выплат звёзд запущена!**\n\n"
                f"🎰 Бот готов отправлять уведомления о выигрышах\n"
                f"💰 Время запуска: {datetime.now().strftime('%H:%M:%S')}\n\n"
                f"Для теста отправьте: /test_payout"
            )
            print("[OK] Тестовое уведомление отправлено\n")
        except Exception as e:
            print(f"[ERROR] Ошибка отправки: {e}\n")

    async def notify_payout(self, user_id: int, username: str, amount: int, combo: str = ""):
        """Уведомление о необходимости выплаты"""
        try:
            message = (
                f"🎰 **ТРЕБУЕТСЯ ВЫПЛАТА!**\n\n"
                f"Игрок: @{username or 'NoUsername'}\n"
                f"ID: `{user_id}`\n"
                f"Сумма: **{amount} звёзд** ⭐\n"
            )

            if combo:
                message += f"Комбинация: {combo}\n"

            message += (
                f"\n**Как выплатить:**\n"
                f"1. Найдите пользователя по ID: `{user_id}`\n"
                f"2. Откройте профиль → Отправить подарок\n"
                f"3. Выберите {amount} звёзд\n"
                f"4. Отправьте"
            )

            await self.app.send_message(ADMIN_ID, message)
            print(f"[OK] Уведомление о выплате {amount} звёзд отправлено")
            return True

        except Exception as e:
            print(f"[ERROR] Ошибка уведомления: {e}")
            return False

async def main():
    """Главная функция"""
    system = SimplePayoutSystem()

    try:
        await system.start()
    except KeyboardInterrupt:
        print("\n\n[!] Остановка системы...")
    except Exception as e:
        print(f"\n[ERROR] Ошибка: {e}")
    finally:
        await system.app.stop()
        print("[!] UserBot остановлен")

if __name__ == "__main__":
    asyncio.run(main())
