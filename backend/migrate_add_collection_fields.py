"""
Миграция: добавление полей collection_id и state в таблицу applications
"""
import sqlite3
import os

# Путь к БД
db_path = os.path.join(os.path.dirname(__file__), "timly.db")

print(f"Подключение к БД: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Проверяем существование полей
    cursor.execute("PRAGMA table_info(applications)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'collection_id' not in columns:
        print("Добавление поля collection_id...")
        cursor.execute("ALTER TABLE applications ADD COLUMN collection_id VARCHAR(50)")
        print("✓ Поле collection_id добавлено")
    else:
        print("✓ Поле collection_id уже существует")

    if 'state' not in columns:
        print("Добавление поля state...")
        cursor.execute("ALTER TABLE applications ADD COLUMN state VARCHAR(50)")
        print("✓ Поле state добавлено")
    else:
        print("✓ Поле state уже существует")

    # Создаем индексы
    print("Создание индексов...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_collection_id ON applications(collection_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_state ON applications(state)")
    print("✓ Индексы созданы")

    conn.commit()
    print("\n✅ Миграция успешно выполнена!")

except Exception as e:
    print(f"\n❌ Ошибка миграции: {e}")
    conn.rollback()
finally:
    conn.close()
