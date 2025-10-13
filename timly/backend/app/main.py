"""
Главный файл FastAPI приложения Timly
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, settings as settings_api, vacancies

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер жизненного цикла приложения
    """
    # Startup
    logger.info("Запуск приложения Timly...")
    
    # Создаём таблицы в БД (для разработки)
    # В продакшене используйте Alembic миграции
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("База данных инициализирована")
    
    yield
    
    # Shutdown
    logger.info("Остановка приложения...")


# Создаём приложение FastAPI
app = FastAPI(
    title="Timly API",
    description="Сервис для анализа откликов с HH.ru с помощью AI",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/api")
app.include_router(settings_api.router, prefix="/api")
app.include_router(vacancies.router, prefix="/api")


@app.get("/")
async def root():
    """
    Корневой endpoint
    """
    return {
        "message": "Добро пожаловать в Timly API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """
    Проверка состояния сервиса
    """
    return {
        "status": "healthy",
        "service": "Timly API"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )