"""
Основной файл приложения Timly
FastAPI приложение с настройкой middleware и маршрутов
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import settings
from app.database import init_database, close_database
from app.api import auth, settings as settings_api, hh_integration, analysis, vacancies, applications, subscription, payment, admin
from app.utils.logger import setup_logging, setup_sentry, get_logger
from app.middleware import register_exception_handlers
from app.middleware.rate_limit import limiter, rate_limit_handler
from slowapi.errors import RateLimitExceeded

# Настройка централизованного логирования
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_file="logs/timly.log" if settings.APP_ENV == "production" else None
)
logger = get_logger(__name__)

# Инициализация Sentry для мониторинга ошибок
setup_sentry()

# Создание FastAPI приложения
app = FastAPI(
    title="Timly API",
    description="AI-powered Resume Screening Platform для российского рынка труда",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Добавляем state для limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Регистрация централизованных обработчиков ошибок
register_exception_handlers(app)

# CORS Middleware - важно для работы фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Trusted Host Middleware для безопасности - ВРЕМЕННО ОТКЛЮЧЕН ДЛЯ ДЕБАГА
# if settings.APP_ENV == "production":
#     app.add_middleware(
#         TrustedHostMiddleware,
#         allowed_hosts=["timly.ru", "*.timly.ru", "api.timly.ru", "188.225.24.157", "localhost"]
#     )


@app.middleware("http")
async def security_headers(request, call_next):
    """Middleware для добавления заголовков безопасности"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    if settings.APP_ENV == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


# События запуска и остановки приложения
@app.on_event("startup")
async def startup_event():
    """Инициализация приложения при старте"""
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode")
    await init_database()

    # Инициализация Telegram сервиса
    try:
        from app.services.telegram_service import get_telegram_service
        telegram_service = get_telegram_service()
        logger.info("Telegram service initialization checked")
    except Exception as e:
        logger.error(f"Error initializing Telegram service: {e}")

    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка ресурсов при остановке"""
    logger.info("Shutting down application")
    await close_database()


# Health check endpoint - требуется по ТЗ
@app.get("/health")
async def health_check():
    """
    Health check endpoint для мониторинга
    Должен отвечать на http://localhost:8000/health
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV
    }


# API Routes - подключение всех роутеров
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["Settings"])
app.include_router(hh_integration.router, prefix="/api/hh", tags=["HH Integration"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(vacancies.router, prefix="/api/vacancies", tags=["Vacancies"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(subscription.router, prefix="/api/subscription", tags=["Subscription"])
app.include_router(payment.router, prefix="/api/payment", tags=["Payment"])
app.include_router(admin.router, tags=["Admin"])


@app.get("/")
async def root():
    """Корневой endpoint с информацией о сервисе"""
    return {
        "message": "Timly API - AI-powered Resume Screening Platform",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )