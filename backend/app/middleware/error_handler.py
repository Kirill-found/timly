"""
Централизованная обработка ошибок для FastAPI
Все исключения преобразуются в стандартный формат APIResponse
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, OperationalError
import traceback

from app.utils.exceptions import (
    TimlyBaseException,
    ValidationError,
    AuthenticationError,
    HHIntegrationError,
    AIAnalysisError,
    DatabaseError,
    CacheError,
    BackgroundJobError
)
from app.utils.response import bad_request, unauthorized, internal_error, not_found
from app.utils.logger import get_logger
from app.config import settings

logger = get_logger(__name__)


async def timly_exception_handler(request: Request, exc: TimlyBaseException) -> JSONResponse:
    """
    Обработчик для всех пользовательских исключений Timly
    """
    logger.warning(
        f"{exc.__class__.__name__}: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "details": exc.details
        }
    )

    # Определяем HTTP статус код по типу исключения
    status_code_map = {
        ValidationError: status.HTTP_400_BAD_REQUEST,
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        HHIntegrationError: status.HTTP_502_BAD_GATEWAY,
        AIAnalysisError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        CacheError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        BackgroundJobError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

    status_code = status_code_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JSONResponse(
        status_code=status_code,
        content={
            "data": None,
            "error": {
                "code": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details if settings.DEBUG else None
            },
            "meta": {
                "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z"
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Обработчик для ошибок валидации Pydantic
    """
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "body": exc.body
        }
    )

    # Форматируем ошибки валидации в читаемый вид
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Ошибка валидации данных",
                "details": {"errors": errors} if settings.DEBUG else None
            },
            "meta": {
                "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z"
            }
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """
    Обработчик для ошибок нарушения целостности БД (unique constraints, foreign keys)
    """
    logger.error(
        f"Database integrity error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )

    # Определяем тип нарушения
    error_msg = str(exc.orig) if hasattr(exc, 'orig') else str(exc)

    if "unique constraint" in error_msg.lower():
        message = "Объект с такими данными уже существует"
        code = "DUPLICATE_ERROR"
    elif "foreign key constraint" in error_msg.lower():
        message = "Связанный объект не найден"
        code = "FOREIGN_KEY_ERROR"
    else:
        message = "Ошибка целостности данных"
        code = "INTEGRITY_ERROR"

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "data": None,
            "error": {
                "code": code,
                "message": message,
                "details": {"original": error_msg} if settings.DEBUG else None
            },
            "meta": {
                "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z"
            }
        }
    )


async def database_error_handler(request: Request, exc: OperationalError) -> JSONResponse:
    """
    Обработчик для ошибок подключения к БД
    """
    logger.error(
        f"Database operational error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "data": None,
            "error": {
                "code": "DATABASE_UNAVAILABLE",
                "message": "Временные проблемы с базой данных. Попробуйте позже.",
                "details": {"original": str(exc)} if settings.DEBUG else None
            },
            "meta": {
                "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z"
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Обработчик для всех непредвиденных исключений
    """
    logger.error(
        f"Unhandled exception: {exc.__class__.__name__}: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc() if settings.DEBUG else None
        },
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "data": None,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Внутренняя ошибка сервера. Мы уже работаем над её устранением.",
                "details": {
                    "type": exc.__class__.__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc()
                } if settings.DEBUG else None
            },
            "meta": {
                "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z"
            }
        }
    )


def register_exception_handlers(app):
    """
    Регистрация всех обработчиков исключений в FastAPI приложении

    Args:
        app: FastAPI application instance
    """
    # Пользовательские исключения Timly
    app.add_exception_handler(TimlyBaseException, timly_exception_handler)

    # Pydantic валидация
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # SQLAlchemy ошибки
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(OperationalError, database_error_handler)

    # Общий обработчик для непредвиденных ошибок
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Exception handlers registered successfully")
