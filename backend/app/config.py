"""
Конфигурация приложения Timly
Централизованное управление настройками с валидацией
"""
from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List
import os


class Settings(BaseSettings):
    """Настройки приложения с валидацией через Pydantic"""

    # Application
    APP_NAME: str = "Timly"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    ENCRYPTION_KEY: str

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # External APIs
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_PROXY_URL: str = ""  # HTTP прокси для OpenAI (необязательно)

    # HH.ru Integration
    HH_MOCK_MODE: bool = False  # Использовать mock данные вместо реального API
    HH_CLIENT_ID: str
    HH_CLIENT_SECRET: str
    HH_REDIRECT_URI: str = "https://timly-hr.ru/auth"

    # URLs
    FRONTEND_URL: str = "https://timly-hr.ru"
    BACKEND_URL: str = "https://timly-hr.ru/api"

    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # Monitoring
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"

    # Payment Systems
    YOOKASSA_SHOP_ID: str = ""  # ID магазина в ЮKassa
    YOOKASSA_SECRET_KEY: str = ""  # Секретный ключ ЮKassa

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = ""  # Токен Telegram бота
    TELEGRAM_ADMIN_CHAT_ID: str = ""  # Chat ID администратора для уведомлений

    # Email SMTP (Timeweb)
    SMTP_HOST: str = "smtp.timeweb.ru"
    SMTP_PORT: int = 465
    SMTP_USER: str = ""  # timly-hr@timly-hr.ru
    SMTP_PASSWORD: str = ""  # Пароль от почты
    SMTP_FROM_EMAIL: str = "timly-hr@timly-hr.ru"
    SMTP_FROM_NAME: str = "Timly"

    @validator('CORS_ORIGINS')
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Парсинг CORS origins из строки"""
        return [origin.strip() for origin in v.split(',')]

    @validator('SECRET_KEY')
    def validate_secret_key(cls, v: str) -> str:
        """Валидация секретного ключа"""
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance
settings = Settings()
