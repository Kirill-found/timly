"""
Скрипт для создания базы данных slot_bot_db
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Параметры подключения к PostgreSQL
DB_HOST = "localhost"
DB_PORT = "5432"
DB_ADMIN_USER = "postgres"
DB_ADMIN_PASSWORD = "1432"

# Параметры новой базы данных
NEW_DB_NAME = "slot_bot_db"
NEW_DB_USER = "slot_bot_user"
NEW_DB_PASSWORD = "myslotbot123"

def create_database():
    """Создание базы данных и пользователя"""
    conn = None
    try:
        # Подключение к PostgreSQL (к базе postgres по умолчанию)
        print("[*] Подключение к PostgreSQL...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_ADMIN_USER,
            password=DB_ADMIN_PASSWORD,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Проверка существования базы данных
        print(f"[*] Проверка существования базы данных '{NEW_DB_NAME}'...")
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (NEW_DB_NAME,)
        )
        exists = cursor.fetchone()

        if exists:
            print(f"[!] База данных '{NEW_DB_NAME}' уже существует!")
        else:
            # Создание базы данных
            print(f"[+] Создание базы данных '{NEW_DB_NAME}'...")
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(NEW_DB_NAME)
                )
            )
            print(f"[+] База данных '{NEW_DB_NAME}' создана успешно!")

        # Проверка существования пользователя
        print(f"[*] Проверка существования пользователя '{NEW_DB_USER}'...")
        cursor.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = %s",
            (NEW_DB_USER,)
        )
        user_exists = cursor.fetchone()

        if user_exists:
            print(f"[!] Пользователь '{NEW_DB_USER}' уже существует!")
        else:
            # Создание пользователя
            print(f"[+] Создание пользователя '{NEW_DB_USER}'...")
            cursor.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                    sql.Identifier(NEW_DB_USER)
                ),
                (NEW_DB_PASSWORD,)
            )
            print(f"[+] Пользователь '{NEW_DB_USER}' создан успешно!")

        # Выдача прав на базу данных
        print(f"[*] Выдача прав пользователю '{NEW_DB_USER}' на базу '{NEW_DB_NAME}'...")
        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier(NEW_DB_NAME),
                sql.Identifier(NEW_DB_USER)
            )
        )
        print(f"[+] Права выданы успешно!")

        cursor.close()
        conn.close()

        # Подключение к новой базе данных для настройки прав на схему
        print(f"[*] Подключение к базе данных '{NEW_DB_NAME}'...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_ADMIN_USER,
            password=DB_ADMIN_PASSWORD,
            database=NEW_DB_NAME
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Выдача прав на схему public
        print(f"[*] Выдача прав на схему public...")
        cursor.execute(
            sql.SQL("GRANT ALL ON SCHEMA public TO {}").format(
                sql.Identifier(NEW_DB_USER)
            )
        )
        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {}").format(
                sql.Identifier(NEW_DB_USER)
            )
        )
        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {}").format(
                sql.Identifier(NEW_DB_USER)
            )
        )
        print(f"[+] Права на схему выданы успешно!")

        cursor.close()

        print("\n" + "="*60)
        print("[+] УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!")
        print("="*60)
        print(f"\n[*] База данных: {NEW_DB_NAME}")
        print(f"[*] Пользователь: {NEW_DB_USER}")
        print(f"[*] Пароль: {NEW_DB_PASSWORD}")
        print(f"\n[*] Connection string:")
        print(f"postgresql://{NEW_DB_USER}:{NEW_DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{NEW_DB_NAME}")
        print("\n[+] Теперь можно запускать бота!")
        print("="*60)

    except psycopg2.Error as e:
        print(f"\n[!] ОШИБКА PostgreSQL: {e}")
        print(f"Код ошибки: {e.pgcode}")
        return False
    except Exception as e:
        print(f"\n[!] ОШИБКА: {e}")
        return False
    finally:
        if conn:
            conn.close()

    return True

if __name__ == "__main__":
    print("="*60)
    print("СОЗДАНИЕ БАЗЫ ДАННЫХ ДЛЯ SLOT BOT")
    print("="*60)
    print()

    success = create_database()

    if success:
        print("\n[+] Всё готово! Запускайте бота командой:")
        print("   python group_slot_bot.py")
    else:
        print("\n[!] Что-то пошло не так. Проверьте:")
        print("   1. PostgreSQL запущен")
        print("   2. Пароль администратора правильный (сейчас: 1432)")
        print("   3. Порт 5432 доступен")
