#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ручная отправка подарка пользователю
Используй когда нужно отправить подарок вручную
"""
import asyncio
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from userbot_manager import UserBotManager

async def send_gift_manually():
    """Ручная отправка подарка"""

    # ПАРАМЕТРЫ - ИЗМЕНИ ПОД СВОЮ СИТУАЦИЮ
    USER_ID = 392792059  # ID пользователя который выиграл
    STARS_AMOUNT = 200   # Сколько Stars отправить (100, 200, 350, 500)

    print("=" * 70)
    print("РУЧНАЯ ОТПРАВКА ПОДАРКА")
    print("=" * 70)
    print()
    print(f"Получатель: {USER_ID}")
    print(f"Сумма: {STARS_AMOUNT} Stars")
    print()

    # Запускаем userbot
    manager = UserBotManager()

    try:
        print("[*] Запуск userbot...")
        await manager.start()

        print(f"[*] Отправка подарка {STARS_AMOUNT} Stars пользователю {USER_ID}...")
        success = await manager.send_gift(
            user_id=USER_ID,
            stars_amount=STARS_AMOUNT
        )

        print()
        if success:
            print("=" * 70)
            print("✅ ПОДАРОК УСПЕШНО ОТПРАВЛЕН!")
            print("=" * 70)
            print()
            print(f"Пользователь {USER_ID} получил {STARS_AMOUNT} Stars")
        else:
            print("=" * 70)
            print("❌ НЕ УДАЛОСЬ ОТПРАВИТЬ ПОДАРОК")
            print("=" * 70)
            print()
            print("Проверь логи выше для деталей ошибки")
            print()
            print("Возможные причины:")
            print("1. STARGIFT_USAGE_LIMITED - аккаунт ограничен")
            print("2. Недостаточно Stars на балансе")
            print("3. Пользователь заблокировал получение подарков")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        await manager.stop()

if __name__ == "__main__":
    asyncio.run(send_gift_manually())
    print()
    input("Нажми Enter чтобы закрыть...")
