#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Авторизация с уже полученным кодом
"""
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
PHONE = "+13188223597"
PASSWORD = "dom32025"  # 2FA пароль если есть

async def auth_with_code():
    print("=" * 70)
    print("АВТОРИЗАЦИЯ С СУЩЕСТВУЮЩИМ КОДОМ")
    print("=" * 70)
    print()

    client = TelegramClient('userbot_session', API_ID, API_HASH)

    try:
        await client.connect()

        if await client.is_user_authorized():
            print("[OK] Уже авторизован!")
            me = await client.get_me()
            print(f"Имя: {me.first_name}")
            print(f"Телефон: {me.phone}")
            return

        # Запрашиваем код (получим phone_code_hash)
        print(f"[*] Запрашиваю код для {PHONE}...")
        sent_code = await client.send_code_request(PHONE)

        print()
        print("=" * 70)
        print(f"Phone Code Hash: {sent_code.phone_code_hash}")
        print("=" * 70)
        print()
        print("ВНИМАНИЕ! Если у тебя уже есть код из предыдущего запроса,")
        print("попробуй ввести его. Telegram иногда не отправляет новый код")
        print("если предыдущий еще действителен.")
        print()

        # Ждем ввод кода
        code = input("Введи код (или 99856 если он еще действителен): ").strip()
        print()
        print(f"[*] Попытка авторизации с кодом {code}...")

        try:
            await client.sign_in(PHONE, code, phone_code_hash=sent_code.phone_code_hash)
            print("[OK] Авторизация успешна!")
        except SessionPasswordNeededError:
            print("[*] Требуется 2FA пароль...")
            print(f"[*] Использую пароль: {PASSWORD}")
            await client.sign_in(password=PASSWORD)
            print("[OK] Авторизация с 2FA успешна!")
        except Exception as e:
            error_msg = str(e)
            if "PHONE_CODE_INVALID" in error_msg:
                print()
                print("[ERROR] Код недействителен или истек!")
                print()
                print("Возможные причины:")
                print("1. Код 99856 уже истек (коды живут ~5-10 минут)")
                print("2. Нужно подождать и получить новый код")
                print("3. Phone code hash изменился")
                print()
                print("Попробуй:")
                print("1. Подожди 10 минут")
                print("2. Запусти скрипт снова")
                print("3. Введи НОВЫЙ код который придет")
            elif "PHONE_CODE_EXPIRED" in error_msg:
                print("[ERROR] Код истек! Нужен новый код.")
            else:
                print(f"[ERROR] Ошибка: {error_msg}")
            raise

        # Проверяем результат
        me = await client.get_me()
        print()
        print("=" * 70)
        print("УСПЕШНАЯ АВТОРИЗАЦИЯ!")
        print("=" * 70)
        print(f"Имя: {me.first_name}")
        print(f"Телефон: {me.phone}")
        print(f"ID: {me.id}")
        if me.username:
            print(f"Username: @{me.username}")
        print()

        # Проверяем подарки
        from telethon.tl.functions.payments import GetStarGiftsRequest

        print("=" * 70)
        print("ПРОВЕРКА КАТАЛОГА ПОДАРКОВ")
        print("=" * 70)
        print()

        result = await client(GetStarGiftsRequest(hash=0))
        gifts = {}

        for gift in result.gifts:
            gifts[gift.stars] = gift.id

        print(f"Найдено подарков: {len(gifts)}")
        print()

        needed = [100, 200, 350, 500]
        print("Для игры:")
        for stars in needed:
            if stars in gifts:
                print(f"  [OK] {stars} Stars - ID: {gifts[stars]}")
            else:
                print(f"  [!!] {stars} Stars - НЕ НАЙДЕНО")
        print()

        print("=" * 70)
        print("ГОТОВО!")
        print("=" * 70)

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(auth_with_code())
    print()
    input("Нажми Enter чтобы закрыть...")
