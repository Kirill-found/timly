"""
Скрипт для сброса пароля пользователя
"""
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def reset_password():
    """Сбросить пароль для test@timly.ru"""
    db = SessionLocal()
    try:
        # Найти пользователя
        user = db.query(User).filter(User.email == "test@timly.ru").first()

        if not user:
            print("Ошибка: Пользователь test@timly.ru не найден")
            return

        # Установить новый пароль
        new_password = "test123"
        user.password_hash = pwd_context.hash(new_password)

        db.commit()

        print(f"Успешно!")
        print(f"Email: test@timly.ru")
        print(f"Пароль: {new_password}")
        print(f"Роль: {user.role}")

    except Exception as e:
        print(f"Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_password()
