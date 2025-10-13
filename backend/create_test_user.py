"""
Создаёт тестового пользователя с известными данными
"""
import sys
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

# Добавляем путь к приложению
sys.path.insert(0, '.')

from app.database import SessionLocal, engine, Base
from app.models import User
from passlib.context import CryptContext

# Настройка bcrypt для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user():
    db = SessionLocal()
    try:
        # ID из токена
        user_id = "04886118-17bf-46db-87bc-2b1dd658080b"
        email = "final@test.com"
        password = "test123"

        # Проверяем, существует ли пользователь
        existing_user = db.query(User).filter(User.id == user_id).first()
        if existing_user:
            print(f"User {email} already exists!")
            return

        # Создаём пользователя
        hashed_password = pwd_context.hash(password)
        user = User(
            id=user_id,
            email=email,
            password_hash=hashed_password,
            role="user",
            company_name="Test Company",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"User created successfully!")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   ID: {user_id}")

    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating test user...")
    create_user()
