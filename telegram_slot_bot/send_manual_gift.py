"""
Скрипт для ручной отправки подарка пользователю
"""
import asyncio
import sys
from userbot_manager import UserBotManager

async def send_gift_manual():
    # ID пользователя @Dtyux из логов
    user_id = 5278295821
    stars_amount = 500  # Джекпот

    print(f"Отправка подарка {stars_amount} Stars пользователю {user_id}...")

    # Инициализируем userbot
    userbot = UserBotManager()
    await userbot.start()

    # Отправляем подарок
    success = await userbot.send_gift(
        user_id=user_id,
        stars_amount=stars_amount
    )

    if success:
        print(f"✅ Подарок {stars_amount} Stars успешно отправлен!")
    else:
        print(f"❌ Не удалось отправить подарок")

    await userbot.stop()

if __name__ == "__main__":
    asyncio.run(send_gift_manual())
