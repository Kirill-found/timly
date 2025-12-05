#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка баланса Telegram Stars на user-bot аккаунте
"""
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.payments import GetStarsStatusRequest

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"

async def check_balance():
    print("=" * 70)
    print("ПРОВЕРКА БАЛАНСА TELEGRAM STARS")
    print("=" * 70)
    print()

    client = TelegramClient('userbot_session', API_ID, API_HASH)

    try:
        await client.connect()

        if not await client.is_user_authorized():
            print("[ERROR] User-bot не авторизован!")
            return

        me = await client.get_me()
        print(f"Аккаунт: {me.first_name} (@{me.username})")
        print(f"ID: {me.id}")
        print()

        # Получаем статус Stars
        print("[*] Получение баланса Stars...")
        stars_status = await client(GetStarsStatusRequest(peer=me))

        print()
        print("=" * 70)
        print("БАЛАНС TELEGRAM STARS")
        print("=" * 70)
        print()
        print(f"[BALANCE] {stars_status.balance} Stars")
        print()

        if stars_status.balance == 0:
            print("[!] ВНИМАНИЕ: Баланс равен 0!")
            print()
            print("Для отправки подарков нужно пополнить Stars:")
            print("  1. Открой Telegram")
            print("  2. Settings → Telegram Stars")
            print("  3. Купи Stars (минимум ~500-1000)")
            print()
            print("Примерные цены:")
            print("  • 50 Stars ~ $1")
            print("  • 500 Stars ~ $10")
            print("  • 1000 Stars ~ $18")
            print()
        else:
            print("✅ Баланс достаточен для отправки подарков!")
            print()
            print("Примерная стоимость выигрышей:")
            print(f"  • 100 Stars × {stars_status.balance // 100} = можно отправить {stars_status.balance // 100} подарков")
            print(f"  • 200 Stars × {stars_status.balance // 200} = можно отправить {stars_status.balance // 200} подарков")
            print(f"  • 500 Stars × {stars_status.balance // 500} = можно отправить {stars_status.balance // 500} подарков")
            print()

        # Проверяем историю транзакций (если доступно)
        if hasattr(stars_status, 'history'):
            print("Последние транзакции:")
            for tx in stars_status.history[:5]:
                print(f"  • {tx}")
            print()

    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(check_balance())
