#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрая авторизация - запросить код и сразу ввести
"""
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
PHONE = "+13188223597"
PASSWORD = "dom32025"  # Если есть 2FA на новом аккаунте

async def quick_auth():
    print("=" * 70)
    print("БЫСТРАЯ АВТОРИЗАЦИЯ USER-BOT")
    print("=" * 70)
    print()

    client = TelegramClient('userbot_session', API_ID, API_HASH)

    try:
        await client.connect()

        if await client.is_user_authorized():
            print("[OK] Уже авторизован!")
            me = await client.get_me()
            print(f"Имя: {me.first_name}")
            print(f"ID: {me.id}")
            await show_gifts(client)
            return

        print(f"[*] Запрашиваю код для {PHONE}...")
        sent_code = await client.send_code_request(PHONE)
        print("[OK] Код отправлен в Telegram!")
        print()
        print("ПРОВЕРЬ TELEGRAM ПРЯМО СЕЙЧАС!")
        print()

        # Ждем ввод кода от пользователя
        code = input("Введи код из Telegram: ").strip()
        print()
        print(f"[*] Ввожу код: {code}")

        try:
            await client.sign_in(PHONE, code, phone_code_hash=sent_code.phone_code_hash)
            print("[OK] Успешно!")
        except SessionPasswordNeededError:
            print("[*] Требуется пароль 2FA...")
            print(f"[*] Ввожу пароль...")
            await client.sign_in(password=PASSWORD)
            print("[OK] Авторизация с паролем успешна!")

        me = await client.get_me()
        print()
        print("=" * 70)
        print("АВТОРИЗАЦИЯ ЗАВЕРШЕНА!")
        print("=" * 70)
        print(f"Имя: {me.first_name}")
        print(f"ID: {me.id}")
        print(f"Username: @{me.username if me.username else 'нет'}")
        print()

        await show_gifts(client)

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()

async def show_gifts(client):
    from telethon.tl.functions.payments import GetStarGiftsRequest

    print("=" * 70)
    print("КАТАЛОГ ПОДАРКОВ")
    print("=" * 70)
    print()

    try:
        result = await client(GetStarGiftsRequest(hash=0))
        gifts = {}

        for gift in result.gifts:
            gifts[gift.stars] = gift.id
            print(f"  [{gift.stars:>4} Stars] ID: {gift.id}")

        print()
        print(f"[OK] Найдено {len(gifts)} подарков")
        print()

        needed = [100, 200, 350, 500]
        print("Для игры:")
        for stars in needed:
            status = "[OK]" if stars in gifts else "[!!]"
            print(f"  {status} {stars} Stars")
        print()

    except Exception as e:
        print(f"[ERROR] Каталог недоступен: {e}")

if __name__ == "__main__":
    asyncio.run(quick_auth())
