"""
База данных и подключения для Timly
Настройки подключения к PostgreSQL с пулом соединений
"""
from sqlalchemy import create_engine, MetaData, TypeDecorator, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.dialects.postgresql import UUID
from app.config import settings
import logging
import uuid

logger = logging.getLogger(__name__)


# Универсальный UUID тип - просто строки для простоты
class GUID(TypeDecorator):
    """Platform-independent GUID type - stores UUIDs as strings"""
    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """При записи в БД - конвертируем UUID в строку"""
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        """При чтении из БД - возвращаем строку как есть (ORM сам создаст UUID)"""
        return value


# Создание движка с оптимизацией для производительности
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite настройки
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # Для SQLite
        echo=settings.DEBUG  # SQL логирование только в dev режиме
    )
else:
    # PostgreSQL настройки
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,  # Уменьшено с 20 до 10 для экономии RAM
        max_overflow=15,  # Уменьшено с 40 до 15
        pool_pre_ping=True,  # Проверка соединений перед использованием
        pool_recycle=3600,  # Пересоздание соединений каждый час
        pool_timeout=30,  # Timeout для получения соединения из пула
        echo=settings.DEBUG  # SQL логирование только в dev режиме
    )

# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей
Base = declarative_base()

# Метаданные для миграций Alembic
metadata = MetaData()


def get_db():
    """
    Dependency injection для получения сессии БД
    Используется в FastAPI endpoints
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_database():
    """
    Инициализация базы данных при старте приложения
    Создает все таблицы если их нет
    """
    try:
        # В production используем Alembic для миграций
        if settings.APP_ENV == "development":
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_database():
    """
    Закрытие соединений при остановке приложения
    """
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")