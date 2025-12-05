"""
Запуск полной системы UserBot + Stars Rewards Bot
"""

import asyncio
from pyrogram import Client
import os
from dotenv import load_dotenv

# Загружаем настройки
load_dotenv()

async def start_system():
    print("\n" + "="*60)
    print("    ЗАПУСК СИСТЕМЫ ВЫПЛАТ ЗВЁЗД")
    print("="*60)

    # Используем существующую сессию
    app = Client(
        "stars_userbot",
        api_id=28668805,
        api_hash="5bd18c34314bf74adfd2066dcc21b2bb"
    )

    try:
        await app.start()

        # Получаем информацию о себе
        me = await app.get_me()
        print(f"\n[OK] UserBot подключен!")
        print(f"Аккаунт: {me.first_name}")
        print(f"ID: {me.id}")

        # Обновляем ADMIN_ID в .env
        env_path = ".env"
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Обновляем существующий ADMIN_ID
            import re
            content = re.sub(r'ADMIN_ID=\d+', f'ADMIN_ID={me.id}', content)

            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"[OK] ADMIN_ID обновлён: {me.id}")

        # Проверяем токен бота
        bot_token = os.getenv("BOT_TOKEN")
        print(f"\n[OK] Токен бота загружен")
        print(f"Бот: {bot_token.split(':')[0]}...")

        # Отправляем тестовое сообщение
        await app.send_message(
            "me",
            f"🎰 **Система выплат звёзд запущена!**\n\n"
            f"✅ UserBot: Активен\n"
            f"✅ Bot Token: Загружен\n"
            f"✅ Admin ID: {me.id}\n\n"
            f"**Готов к приёму выплат звёзд!**"
        )
        print("\n[OK] Уведомление отправлено в Избранное")

        print("\n" + "="*60)
        print("    СИСТЕМА ГОТОВА К РАБОТЕ!")
        print("="*60)

        print("\n=== КАК РАБОТАТЬ ===")
        print("1. Когда игрок выиграет, вам придёт уведомление")
        print("2. Откройте чат с победителем")
        print("3. Нажмите меню -> Подарить звёзды")
        print("4. Выберите нужное количество")
        print("5. Подтвердите в боте")

        print("\n=== ЭКОНОМИКА ===")
        print("Ставка: 15 звёзд = 31.5 рублей")
        print("При RTP 95%: прибыль 0.75 звёзд с игры")
        print("100 игр = 75 звёзд прибыли (157 рублей)")

        print("\n=== ВАЖНО ===")
        print("- Держите баланс звёзд на аккаунте")
        print("- Или привяжите карту для автопокупки")
        print("- Начните с малых ставок для теста")

        print("\n[!] Теперь запустите основной бот:")
        print("python channel_integration.py")

        # Держим соединение активным
        print("\nНажмите Ctrl+C для выхода...")
        while True:
            await asyncio.sleep(60)

    except KeyboardInterrupt:
        print("\n\nОстановка системы...")
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
    finally:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(start_system())