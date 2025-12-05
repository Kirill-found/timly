"""
Rate limiting middleware для защиты от перегрузки API
Ограничение количества запросов анализа на пользователя
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status
from functools import wraps
import time
from typing import Callable
import redis
from app.config import settings

# Инициализация limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri=settings.REDIS_URL if hasattr(settings, 'REDIS_URL') else "memory://"
)

# Rate limit для анализа (более строгий)
analysis_limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["5/minute"],  # 5 запусков анализа в минуту
    storage_uri=settings.REDIS_URL if hasattr(settings, 'REDIS_URL') else "memory://"
)


def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom обработчик превышения rate limit
    """
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "RATE_LIMIT_EXCEEDED",
            "message": "Превышен лимит запросов. Пожалуйста, подождите немного.",
            "retry_after": exc.retry_after if hasattr(exc, 'retry_after') else 60
        }
    )
