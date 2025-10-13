"""
Helper функции для создания API responses
Согласно TECHNICAL.md формат: {"data": {...}, "error": null, "meta": {"timestamp": "..."}}
"""
from typing import Any, Optional, Dict
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

from app.schemas.base import APIResponse, APIError, APIErrorDetails, APIResponseMeta


def create_success_response(
    data: Any = None,
    status_code: int = 200
) -> JSONResponse:
    """
    Создание успешного API response

    Args:
        data: Данные для возврата
        status_code: HTTP status code

    Returns:
        JSONResponse в формате TECHNICAL.md
    """
    response_data = APIResponse(
        data=data,
        error=None,
        meta=APIResponseMeta()
    )

    return JSONResponse(
        content=response_data.model_dump(),
        status_code=status_code
    )


def create_error_response(
    code: str,
    message: str,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None,
    field: Optional[str] = None,
    reason: Optional[str] = None
) -> JSONResponse:
    """
    Создание error API response

    Args:
        code: Код ошибки (например, "INVALID_CREDENTIALS")
        message: Сообщение об ошибке
        status_code: HTTP status code
        details: Дополнительные детали ошибки
        field: Поле, вызвавшее ошибку
        reason: Причина ошибки

    Returns:
        JSONResponse в формате TECHNICAL.md
    """
    error_details = None
    if details or field or reason:
        error_details = APIErrorDetails(
            field=field,
            reason=reason,
            code=details.get('code') if details else None
        )

    error = APIError(
        code=code,
        message=message,
        details=error_details
    )

    response_data = APIResponse(
        data=None,
        error=error,
        meta=APIResponseMeta()
    )

    return JSONResponse(
        content=response_data.model_dump(),
        status_code=status_code
    )


def handle_http_exception(exc: HTTPException) -> JSONResponse:
    """
    Обработчик HTTPException для единого формата ошибок

    Args:
        exc: HTTPException

    Returns:
        JSONResponse в формате TECHNICAL.md
    """
    # Попытка извлечь структурированные данные из detail
    if isinstance(exc.detail, dict):
        code = exc.detail.get('error', 'UNKNOWN_ERROR')
        message = exc.detail.get('message', str(exc.detail))
        details = exc.detail.get('details')
    else:
        # Если detail - строка, создаем базовую структуру
        message = str(exc.detail)

        # Определяем код ошибки по статусу
        status_to_code = {
            400: 'BAD_REQUEST',
            401: 'UNAUTHORIZED',
            403: 'FORBIDDEN',
            404: 'NOT_FOUND',
            409: 'CONFLICT',
            422: 'VALIDATION_ERROR',
            429: 'RATE_LIMIT_EXCEEDED',
            500: 'INTERNAL_SERVER_ERROR',
            503: 'SERVICE_UNAVAILABLE'
        }
        code = status_to_code.get(exc.status_code, 'UNKNOWN_ERROR')
        details = None

    return create_error_response(
        code=code,
        message=message,
        status_code=exc.status_code,
        details=details
    )


# Convenience функции для частых случаев
def success(data: Any = None) -> JSONResponse:
    """Быстрое создание success response"""
    return create_success_response(data)


def created(data: Any = None) -> JSONResponse:
    """Success response для создания ресурса"""
    return create_success_response(data, status_code=201)


def bad_request(message: str, code: str = "BAD_REQUEST", field: str = None) -> JSONResponse:
    """Bad request error response"""
    return create_error_response(
        code=code,
        message=message,
        status_code=400,
        field=field
    )


def unauthorized(message: str = "Unauthorized", code: str = "UNAUTHORIZED") -> JSONResponse:
    """Unauthorized error response"""
    return create_error_response(
        code=code,
        message=message,
        status_code=401
    )


def not_found(message: str = "Resource not found", code: str = "NOT_FOUND") -> JSONResponse:
    """Not found error response"""
    return create_error_response(
        code=code,
        message=message,
        status_code=404
    )


def internal_error(message: str = "Internal server error", code: str = "INTERNAL_SERVER_ERROR") -> JSONResponse:
    """Internal server error response"""
    return create_error_response(
        code=code,
        message=message,
        status_code=500
    )