"""
Скрипт для добавления таблицы pending_payouts в базу данных
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Загрузка переменных окружения
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS pending_payouts (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    username VARCHAR(255),

    -- Детали выигрыша
    amount INTEGER NOT NULL,
    dice_value INTEGER,
    combination VARCHAR(50),

    -- Статус выплаты
    status VARCHAR(20) DEFAULT 'pending',

    -- Временные метки
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP,

    -- Дополнительная информация
    attempts INTEGER DEFAULT 0,
    last_error TEXT,
    transaction_id INTEGER,
    admin_note TEXT
);

-- Индексы для ускорения поиска
CREATE INDEX IF NOT EXISTS idx_pending_payouts_user_id ON pending_payouts(user_id);
CREATE INDEX IF NOT EXISTS idx_pending_payouts_status ON pending_payouts(status);
CREATE INDEX IF NOT EXISTS idx_pending_payouts_created_at ON pending_payouts(created_at);
"""

if __name__ == "__main__":
    print("="*60)
    print("ДОБАВЛЕНИЕ ТАБЛИЦЫ PENDING_PAYOUTS")
    print("="*60)
    print()

    if not DATABASE_URL:
        print("[!] ОШИБКА: DATABASE_URL не найден в .env файле!")
        exit(1)

    print(f"[*] Подключение к базе данных...")
    print()

    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect() as conn:
            print("[*] Создание таблицы pending_payouts...")
            conn.execute(text(CREATE_TABLE_SQL))
            conn.commit()
            print("[+] Таблица успешно создана!")

        print()
        print("="*60)
        print("[+] МИГРАЦИЯ ЗАВЕРШЕНА!")
        print("="*60)
        print()
        print("[*] Добавлена таблица:")
        print("    - pending_payouts (выплаты выигрышей)")
        print()
        print("[+] Теперь можно запускать:")
        print("    1. python group_slot_bot.py  (игровой бот)")
        print("    2. python admin_payout_bot.py  (админ-бот для выплат)")
        print()

    except Exception as e:
        print(f"[!] ОШИБКА: {e}")
        exit(1)
