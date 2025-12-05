"""
Скрипт для добавления полей TON в существующие таблицы
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Загрузка переменных окружения
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

ADD_FIELDS_SQL = """
-- Добавление полей TON в таблицу users
ALTER TABLE users
ADD COLUMN IF NOT EXISTS ton_address VARCHAR(255),
ADD COLUMN IF NOT EXISTS ton_address_verified BOOLEAN DEFAULT FALSE;

-- Добавление полей TON транзакций в таблицу transactions
ALTER TABLE transactions
ADD COLUMN IF NOT EXISTS ton_transaction_hash VARCHAR(255),
ADD COLUMN IF NOT EXISTS ton_amount FLOAT,
ADD COLUMN IF NOT EXISTS ton_destination VARCHAR(255),
ADD COLUMN IF NOT EXISTS ton_status VARCHAR(50);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_users_ton_address ON users(ton_address);
CREATE INDEX IF NOT EXISTS idx_transactions_ton_hash ON transactions(ton_transaction_hash);
CREATE INDEX IF NOT EXISTS idx_transactions_ton_status ON transactions(ton_status);
"""

if __name__ == "__main__":
    print("="*60)
    print("ДОБАВЛЕНИЕ ПОЛЕЙ TON В БАЗУ ДАННЫХ")
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
            print("[*] Добавление полей TON...")
            conn.execute(text(ADD_FIELDS_SQL))
            conn.commit()
            print("[+] Поля успешно добавлены!")

        print()
        print("="*60)
        print("[+] МИГРАЦИЯ ЗАВЕРШЕНА!")
        print("="*60)
        print()
        print("[*] Добавлены поля:")
        print("    Users:")
        print("      - ton_address (TON адрес пользователя)")
        print("      - ton_address_verified (подтверждение адреса)")
        print()
        print("    Transactions:")
        print("      - ton_transaction_hash (hash транзакции)")
        print("      - ton_amount (сумма в TON)")
        print("      - ton_destination (адрес получателя)")
        print("      - ton_status (статус: pending/confirmed/failed)")
        print()
        print("[+] Теперь можно настроить TON кошелек в .env файле")
        print()

    except Exception as e:
        print(f"[!] ОШИБКА: {e}")
        exit(1)
