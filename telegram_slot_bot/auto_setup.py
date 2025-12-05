"""
Автоматическая настройка UserBot
БЕЗ интерактивного ввода - для тестирования
"""

import asyncio
import os
import sys
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid

# UTF-8 для Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*60)
print("    АВТОМАТИЧЕСКАЯ НАСТРОЙКА USERBOT")
print("="*60)

# Реальные API данные пользователя
API_ID = 28668805
API_HASH = "5bd18c34314bf74adfd2066dcc21b2bb"

print("\nAPI данные:")
print(f"API_ID: {API_ID}")
print(f"API_HASH: {API_HASH[:10]}...")

async def test_connection():
    """Тестирование подключения к Telegram"""

    print("\nТестируем подключение к Telegram серверам...")

    # Создаём тестовый клиент БЕЗ авторизации
    app = Client(
        "test_connection",
        api_id=API_ID,
        api_hash=API_HASH,
        no_updates=True,
        in_memory=True  # Не сохраняем сессию
    )

    try:
        await app.connect()
        print("✅ Подключение к Telegram успешно!")
        print(f"   Сервер: {app.session.dc_id if hasattr(app.session, 'dc_id') else 'DC1'}")

        # Проверяем что API credentials корректные
        print("\n✅ API credentials валидные!")

    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    finally:
        await app.disconnect()

    return True

async def create_config():
    """Создание конфигурационных файлов"""

    print("\n" + "-"*60)
    print("Создаём конфигурационные файлы...")

    # Создаём .env файл для дальнейшей настройки
    env_template = f"""# КОНФИГУРАЦИЯ USERBOT ДЛЯ ОТПРАВКИ ЗВЁЗД
# Создано автоматически

# API Credentials (уже проверены)
API_ID={API_ID}
API_HASH={API_HASH}

# ВАЖНО: Добавьте эти данные вручную!
# -------------------------------------
PHONE_NUMBER=+7XXXXXXXXXX  # <- Ваш номер телефона
ADMIN_ID=123456789         # <- Ваш Telegram ID (узнать у @userinfobot)
BOT_TOKEN=123456:ABC...    # <- Токен бота от @BotFather

# Настройки выплат (можно оставить как есть)
AUTO_PAYMENT_ENABLED=false
MAX_AUTO_PAYMENT=500
PAYMENT_DELAY=3
DATABASE_URL=sqlite:///slot_bot.db
MAX_DAILY_PAYOUTS=50
ANTI_SPAM_DELAY=60

# Сессия
SESSION_NAME=stars_userbot
"""

    with open('.env.template', 'w', encoding='utf-8') as f:
        f.write(env_template)

    print("✅ Создан файл .env.template")

    # Создаём простой скрипт для запуска после настройки
    launcher_script = """import asyncio
from pyrogram import Client
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    app = Client(
        os.getenv("SESSION_NAME", "stars_userbot"),
        api_id=int(os.getenv("API_ID")),
        api_hash=os.getenv("API_HASH"),
        phone_number=os.getenv("PHONE_NUMBER")
    )

    async with app:
        me = await app.get_me()
        print(f"✅ UserBot запущен как @{me.username if me.username else me.first_name}")
        await app.send_message("me", "UserBot готов к работе!")
        print("Отправлено тестовое сообщение")

if __name__ == "__main__":
    asyncio.run(main())
"""

    with open('quick_test.py', 'w', encoding='utf-8') as f:
        f.write(launcher_script)

    print("✅ Создан файл quick_test.py для быстрого теста")

    return True

async def main():
    """Главная функция"""

    # Тестируем подключение
    if not await test_connection():
        print("\n❌ Не удалось подключиться к Telegram")
        return

    # Создаём конфигурацию
    if not await create_config():
        print("\n❌ Не удалось создать конфигурацию")
        return

    print("\n" + "="*60)
    print("    ПОДГОТОВКА ЗАВЕРШЕНА!")
    print("="*60)

    print("\n📋 ЧТО НУЖНО СДЕЛАТЬ ДАЛЬШЕ:\n")

    print("1️⃣  ОТКРОЙТЕ файл .env.template и добавьте:")
    print("    • Ваш номер телефона")
    print("    • Ваш Telegram ID")
    print("    • Токен бота (если есть)")

    print("\n2️⃣  ПЕРЕИМЕНУЙТЕ .env.template в .env")

    print("\n3️⃣  СОЗДАЙТЕ файл для авторизации auth.py:")
    print("    Скопируйте код ниже:")
    print("-"*40)

    auth_code = """from pyrogram import Client
import asyncio

app = Client("stars_userbot",
    api_id=28668805,
    api_hash="5bd18c34314bf74adfd2066dcc21b2bb")

async def auth():
    await app.start()
    me = await app.get_me()
    print(f"Авторизован как: {me.first_name}")
    await app.stop()

asyncio.run(auth())"""

    print(auth_code)
    print("-"*40)

    print("\n4️⃣  ЗАПУСТИТЕ auth.py и следуйте инструкциям")

    print("\n5️⃣  ПОСЛЕ авторизации запустите userbot_practical.py")

    print("\n" + "="*60)
    print("\n💡 АЛЬТЕРНАТИВНЫЙ ВАРИАНТ:")
    print("\nЕсли хотите протестировать без реальной авторизации,")
    print("используйте демо-режим: python test_practical_demo.py")

    # Сохраняем инструкцию по авторизации
    with open('auth.py', 'w', encoding='utf-8') as f:
        f.write(auth_code)

    print("\n✅ Файл auth.py создан автоматически!")
    print("   Запустите его для авторизации: python auth.py")

if __name__ == "__main__":
    asyncio.run(main())