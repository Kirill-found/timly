#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Авторизация user-bot с кодом 26228
"""
import asyncio
from telethon import TelegramClient

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
PHONE = "+13188223597"
CODE = "99856"  # Код из Telegram
PASSWORD = None  # Нет 2FA на этом аккаунте

async def authorize():
    print("=" * 70)
    print("АВТОРИЗАЦИЯ USER-BOT")
    print("=" * 70)
    print()
    print(f"Телефон: {PHONE}")
    print(f"Код: {CODE}")
    print()

    client = TelegramClient('userbot_session', API_ID, API_HASH)

    try:
        print("[*] Подключаюсь к Telegram...")
        await client.connect()

        if not await client.is_user_authorized():
            print("[*] Отправляю код авторизации...")

            # Отправляем запрос на код
            await client.send_code_request(PHONE)

            # Вводим код
            print(f"[*] Ввожу код: {CODE}")

            try:
                await client.sign_in(PHONE, CODE)
                print("[OK] Авторизация успешна!")
            except Exception as e:
                if "SessionPasswordNeededError" in str(type(e).__name__):
                    if PASSWORD:
                        print("[*] Требуется пароль 2FA...")
                        print(f"[*] Ввожу пароль...")
                        await client.sign_in(password=PASSWORD)
                        print("[OK] Авторизация с паролем успешна!")
                    else:
                        print("[ERROR] Требуется пароль 2FA, но он не указан!")
                        raise
                else:
                    raise
        else:
            print("[OK] Уже авторизован!")

        # Проверяем что авторизовались
        me = await client.get_me()
        print()
        print("=" * 70)
        print("ИНФОРМАЦИЯ О USER-BOT")
        print("=" * 70)
        print(f"Имя: {me.first_name}")
        if me.last_name:
            print(f"Фамилия: {me.last_name}")
        if me.username:
            print(f"Username: @{me.username}")
        print(f"ID: {me.id}")
        print(f"Телефон: {me.phone}")
        print()

        # Проверяем каталог подарков
        print("=" * 70)
        print("ПРОВЕРКА КАТАЛОГА ПОДАРКОВ")
        print("=" * 70)
        print()

        from telethon.tl.functions.payments import GetStarGiftsRequest

        try:
            print("[*] Загружаю каталог подарков через MTProto...")
            result = await client(GetStarGiftsRequest(hash=0))

            gifts = {}
            for gift in result.gifts:
                gifts[gift.stars] = gift.id
                print(f"  [{gift.stars:>4} Stars] -> Gift ID: {gift.id}")

            print()
            print(f"[OK] Найдено {len(gifts)} подарков в каталоге!")
            print()

            # Проверяем что нужно для игры
            needed = [100, 200, 350, 500]
            print("Проверка для нашей игры:")
            for stars in needed:
                if stars in gifts:
                    print(f"  [OK] {stars} Stars - ДОСТУПНО (ID: {gifts[stars]})")
                else:
                    print(f"  [!!] {stars} Stars - НЕ НАЙДЕНО")
            print()

        except Exception as e:
            print(f"[ERROR] Ошибка загрузки каталога: {e}")
            import traceback
            traceback.print_exc()

        print("=" * 70)
        print("АВТОРИЗАЦИЯ ЗАВЕРШЕНА!")
        print("=" * 70)
        print()
        print("Файл 'userbot_session.session' создан!")
        print("Теперь можно запускать user-bot без повторной авторизации")
        print()

    except Exception as e:
        print()
        print("[ERROR] Ошибка авторизации!")
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.disconnect()
        print("[*] Отключено от Telegram")

if __name__ == "__main__":
    asyncio.run(authorize())
