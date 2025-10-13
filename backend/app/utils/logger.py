"""
Централизованная система логирования для Timly
Структурированные логи с поддержкой Sentry
"""
import logging
import sys
from typing import Optional
from pathlib import Path

from app.config import settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Настройка централизованного логирования

    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
        log_file: Путь к файлу логов (опционально)

    Returns:
        logging.Logger: Настроенный корневой логгер
    """
    level = log_level or settings.LOG_LEVEL

    # Создаем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Очищаем существующие handlers
    root_logger.handlers.clear()

    # Формат для структурированных логов
    log_format = (
        '%(asctime)s | %(levelname)-8s | %(name)s | '
        '%(funcName)s:%(lineno)d | %(message)s'
    )
    formatter = logging.Formatter(
        log_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console Handler (stdout для INFO+, stderr для WARNING+)
    # Обертка для UTF-8 на Windows
    import io
    import platform

    if platform.system() == 'Windows':
        # На Windows оборачиваем stdout в TextIOWrapper с UTF-8
        try:
            stdout_stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        except AttributeError:
            # Если buffer недоступен (например в некоторых IDE)
            stdout_stream = sys.stdout
    else:
        stdout_stream = sys.stdout

    console_handler = logging.StreamHandler(stdout_stream)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File Handler (если указан файл)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Настройка уровней для сторонних библиотек
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Получить логгер для модуля

    Args:
        name: Имя модуля (обычно __name__)

    Returns:
        logging.Logger: Настроенный логгер
    """
    return logging.getLogger(name)


def setup_sentry():
    """
    Настройка Sentry для мониторинга ошибок в production
    """
    if settings.SENTRY_DSN and settings.APP_ENV == "production":
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.APP_ENV,
            traces_sample_rate=0.1,  # 10% трассировка для performance
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            # Фильтрация чувствительных данных
            before_send=lambda event, hint: filter_sensitive_data(event),
        )

        logger = get_logger(__name__)
        logger.info(f"Sentry initialized for {settings.APP_ENV} environment")


def filter_sensitive_data(event):
    """
    Фильтрация чувствительных данных из Sentry событий
    """
    # Удаляем пароли, токены и другие чувствительные данные
    if 'request' in event:
        request = event['request']

        # Фильтруем headers
        if 'headers' in request:
            sensitive_headers = ['authorization', 'cookie', 'x-api-key']
            for header in sensitive_headers:
                if header in request['headers']:
                    request['headers'][header] = '[FILTERED]'

        # Фильтруем body
        if 'data' in request:
            sensitive_fields = ['password', 'token', 'secret', 'hh_token']
            data = request.get('data', {})
            if isinstance(data, dict):
                for field in sensitive_fields:
                    if field in data:
                        data[field] = '[FILTERED]'

    return event


class LoggerContext:
    """
    Контекстный менеджер для логирования с дополнительным контекстом

    Usage:
        with LoggerContext(logger, user_id=user.id):
            logger.info("Processing request")
    """

    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.old_factory = None

    def __enter__(self):
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record

        self.old_factory = logging.getLogRecordFactory()
        logging.setLogRecordFactory(record_factory)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)
