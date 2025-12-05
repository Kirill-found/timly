#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интерактивная авторизация нового user-bot аккаунта
ЗАПУСКАТЬ В POWERSHELL ВРУЧНУЮ!
"""
import asyncio
import sys
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"

print("=" * 70)
print("АВТОРИЗАЦИЯ НОВОГО USER-BOT АККАУНТА")
print("=" * 70)
print()

# Запрашиваем номер у пользователя
phone = input("Введи номер телефона (например +79991234567): ").strip()
if not phone.startswith("+"):
    phone = "+" + phone

print()
print(f"Используем номер: {phone}")
print()
print("ВАЖНО:")
print("1. Сейчас Telegram отправит КОД на этот номер")
print("2. Проверь Telegram и введи код здесь")
print("3. Если есть 2FA - нужно будет ввести пароль")
print()
input("Нажми Enter чтобы продолжить...")
print()

async def main():
    client = TelegramClient('userbot_session', API_ID, API_HASH)

    try:
        await client.connect()

        if not await client.is_user_authorized():
            print("[*] Отправляю запрос на код...")
            await client.send_code_request(phone)

            print()
            print("=" * 70)
            print("КОД ОТПРАВЛЕН!")
            print("=" * 70)
            print()
            print(f"Проверь Telegram на номере {phone}")
            print("Там должно прийти сообщение с кодом")
            print()

            # Ждем ввод кода
            code = input("Введи код из Telegram: ").strip()

            print()
            print(f"[*] Ввожу код: {code}")

            try:
                await client.sign_in(phone, code)
                print("[OK] Успешно!")
            except SessionPasswordNeededError:
                print()
                print("[!] Требуется пароль 2FA")
                password = input("Введи пароль 2FA: ").strip()
                print()
                print("[*] Ввожу пароль...")
                await client.sign_in(password=password)
                print("[OK] Успешно!")
        else:
            print("[OK] Уже авторизован!")

        # Проверяем кто авторизован
        me = await client.get_me()
        print()
        print("=" * 70)
        print("АВТОРИЗОВАН!")
        print("=" * 70)
        print(f"Имя: {me.first_name}")
        if me.last_name:
            print(f"Фамилия: {me.last_name}")
        if me.username:
            print(f"Username: @{me.username}")
        print(f"ID: {me.id}")
        print(f"Телефон: {me.phone}")
        print()

        # Проверяем подарки
        print("=" * 70)
        print("ПРОВЕРКА КАТАЛОГА ПОДАРКОВ")
        print("=" * 70)
        print()

        from telethon.tl.functions.payments import GetStarGiftsRequest

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
                print(f"  [OK] {stars} Stars - ДОСТУПНО (ID: {gifts[stars]})")
            else:
                print(f"  [!!] {stars} Stars - НЕ НАЙДЕНО")
        print()

        print("=" * 70)
        print("ГОТОВО!")
        print("=" * 70)
        print()
        print("User-bot настроен и готов к работе!")
        print("Файл 'userbot_session.session' создан")
        print()

    except Exception as e:
        print()
        print("[ERROR] Ошибка:")
        print(e)
        import traceback
        traceback.print_exc()

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
    print()
    input("Нажми Enter чтобы закрыть...")
