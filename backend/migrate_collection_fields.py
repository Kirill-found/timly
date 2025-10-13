"""
Миграция БД: добавление полей collection_id и state
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "timly.db")

if not os.path.exists(db_path):
    print("БД не существует, будет создана при запуске приложения")
    exit(0)

print(f"Подключение к БД: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Проверяем существование таблицы
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='applications'")
    if not cursor.fetchone():
        print("Таблица applications не существует, пропускаем миграцию")
        conn.close()
        exit(0)

    # Проверяем существование полей
    cursor.execute("PRAGMA table_info(applications)")
    columns = {row[1] for row in cursor.fetchall()}

    changes_made = False

    if 'collection_id' not in columns:
        print("Добавление поля collection_id...")
        cursor.execute("ALTER TABLE applications ADD COLUMN collection_id VARCHAR(50)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_collection_id ON applications(collection_id)")
        print("✓ Поле collection_id добавлено")
        changes_made = True
    else:
        print("✓ Поле collection_id уже существует")

    if 'state' not in columns:
        print("Добавление поля state...")
        cursor.execute("ALTER TABLE applications ADD COLUMN state VARCHAR(50)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_state ON applications(state)")
        print("✓ Поле state добавлено")
        changes_made = True
    else:
        print("✓ Поле state уже существует")

    if changes_made:
        conn.commit()
        print("\n✅ Миграция успешно выполнена!")
    else:
        print("\n✅ Миграция не требуется, все поля уже существуют")

except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    conn.rollback()
finally:
    conn.close()
