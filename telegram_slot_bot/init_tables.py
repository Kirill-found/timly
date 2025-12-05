"""
Скрипт для инициализации таблиц в базе данных
"""
import os
from dotenv import load_dotenv
from database import Database

# Загрузка переменных окружения
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if __name__ == "__main__":
    print("="*60)
    print("ИНИЦИАЛИЗАЦИЯ ТАБЛИЦ В БАЗЕ ДАННЫХ")
    print("="*60)
    print()

    if not DATABASE_URL:
        print("[!] ОШИБКА: DATABASE_URL не найден в .env файле!")
        exit(1)

    print(f"[*] Подключение к базе данных...")
    print(f"[*] URL: {DATABASE_URL}")
    print()

    try:
        # Инициализация базы данных (автоматически создаст таблицы)
        db = Database(DATABASE_URL)

        print("[+] Таблицы успешно созданы!")
        print()
        print("="*60)
        print("[+] ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА!")
        print("="*60)
        print()
        print("[*] Список созданных таблиц:")
        print("    - users (пользователи)")
        print("    - transactions (транзакции)")
        print("    - achievements (достижения)")
        print("    - user_achievements (достижения пользователей)")
        print("    - payments (платежи)")
        print("    - game_stats (игровая статистика)")
        print("    - dice_value_mappings (маппинг значений кубика)")
        print()
        print("[+] Теперь можно запускать бота!")
        print("   python group_slot_bot.py")

    except Exception as e:
        print(f"[!] ОШИБКА: {e}")
        exit(1)
