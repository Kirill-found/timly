"""
Конфигурация pytest для тестов Timly
Настройка фикстур, тестовой БД и общих моков
"""
import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, AsyncMock, patch

# Импорты приложения
from app.main import app
from app.database import get_db, Base
from app.models.user import User


# Настройка тестовой базы данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_timly.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override для подключения к тестовой БД"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Настройка тестовой базы данных для всей сессии"""
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)

    # Переопределяем зависимость БД
    app.dependency_overrides[get_db] = override_get_db

    yield

    # Очистка
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def db():
    """Фикстура для работы с тестовой БД"""
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()


@pytest.fixture
def client():
    """Фикстура для HTTP клиента FastAPI"""
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def clean_db():
    """Очистка БД перед каждым тестом"""
    database = TestingSessionLocal()
    try:
        # Удаляем всех пользователей перед каждым тестом
        database.query(User).delete()
        database.commit()
        yield
    finally:
        database.close()


@pytest.fixture
def mock_hh_client():
    """Мок для HH API клиента"""
    with patch('app.services.hh_client.HHClient') as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance

        # По умолчанию возвращаем успешную валидацию
        mock_instance.test_connection.return_value = {
            "is_valid": True,
            "employer_name": "Test Employer"
        }

        yield mock_instance


@pytest.fixture
def test_user_data():
    """Данные для создания тестового пользователя"""
    return {
        "email": "test@testcompany.ru",
        "password": "TestPassword123",
        "company_name": "ООО Тестовая Компания"
    }


@pytest.fixture
def authenticated_client(client, test_user_data):
    """Аутентифицированный клиент"""
    # Регистрация
    client.post("/api/auth/register", json=test_user_data)

    # Логин
    login_response = client.post("/api/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })

    token = login_response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    return client


@pytest.fixture
def russian_test_data():
    """Тестовые данные с кириллицей"""
    return {
        "valid_names": [
            "Иван Иванов",
            "Мария Петрова-Сидорова",
            "Александр Македонский",
        ],
        "companies": [
            "ООО «Яндекс»",
            "АО \"Сбербанк\"",
            "ПАО 'Газпром'",
        ],
        "emails": [
            "ivan@яндекс.рф",
            "maria@test-компания.рус",
        ]
    }


# Настройка логирования для тестов
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


# Маркеры для тестов
pytest.mark.auth = pytest.mark.auth
pytest.mark.security = pytest.mark.security
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow