#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для первичной настройки и авторизации User-bot
Запустите этот скрипт ОДИН РАЗ для авторизации
"""
import asyncio
import sys
import os

# Настройка UTF-8 для Windows
if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

from userbot_gift_sender import UserBotGiftSender

# Твои данные из my.telegram.org
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
PHONE = "+12678413919"

async def main():
    print("=" * 70)
    print("🚀 ПЕРВИЧНАЯ НАСТРОЙКА USER-BOT")
    print("=" * 70)
    print()
    print(f"📱 Телефон: {PHONE}")
    print(f"🔑 API ID: {API_ID}")
    print(f"🔑 API Hash: {API_HASH[:10]}...")
    print()
    print("⚠️  ВАЖНО: Тебе придет КОД в Telegram на номер " + PHONE)
    print("   После этого нужно будет ввести код здесь в терминале")
    print()

    sender = UserBotGiftSender(API_ID, API_HASH, PHONE)

    try:
        print("🔌 Подключаюсь к Telegram...")
        await sender.start()

        print()
        print("=" * 70)
        print("✅ АВТОРИЗАЦИЯ УСПЕШНА!")
        print("=" * 70)
        print()
        print("Информация о user-bot:")
        me = await sender.client.get_me()
        print(f"  👤 Имя: {me.first_name}")
        print(f"  🆔 ID: {me.id}")
        print(f"  📱 Телефон: {me.phone}")
        print()

        print("=" * 70)
        print("📦 КАТАЛОГ ПОДАРКОВ")
        print("=" * 70)
        print()

        if sender._gifts_cache:
            print("✅ Каталог подарков загружен!")
            print()
            print("Доступные подарки:")
            for stars, gift_id in sorted(sender._gifts_cache.items()):
                print(f"  ⭐ {stars:>4} Stars → Gift ID: {gift_id}")
            print()

            # Проверяем что нужно для игры
            needed = [100, 200, 350, 500]
            print("Проверка для нашей игры:")
            for stars in needed:
                if stars in sender._gifts_cache:
                    print(f"  ✅ {stars} Stars - ДОСТУПНО")
                else:
                    print(f"  ❌ {stars} Stars - НЕ НАЙДЕНО")
            print()

        print("=" * 70)
        print("🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
        print("=" * 70)
        print()
        print("Что дальше:")
        print("  1. Файл 'userbot_session.session' создан - НЕ УДАЛЯЙ ЕГО!")
        print("  2. Теперь можно интегрировать user-bot с основным ботом")
        print("  3. User-bot будет отправлять подарки победителям")
        print()

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ОШИБКА!")
        print("=" * 70)
        print(f"Ошибка: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False

    finally:
        await sender.stop()

    return True

if __name__ == "__main__":
    print()
    result = asyncio.run(main())

    if result:
        print("✅ Все готово! Можно запускать бота!")
        sys.exit(0)
    else:
        print("❌ Что-то пошло не так. Проверь настройки.")
        sys.exit(1)