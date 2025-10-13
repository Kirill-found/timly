"""
Утилиты валидации для Timly
Дополнительные валидаторы для данных
"""
import re
from typing import Any, Optional
import uuid


def is_valid_uuid(value: str) -> bool:
    """
    Проверка корректности UUID строки

    Args:
        value: Строка для проверки

    Returns:
        bool: True если валидный UUID
    """
    try:
        uuid.UUID(value)
        return True
    except (ValueError, TypeError):
        return False


def is_valid_email(email: str) -> bool:
    """
    Базовая проверка email адреса

    Args:
        email: Email для проверки

    Returns:
        bool: True если email валиден
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """
    Проверка российского номера телефона

    Args:
        phone: Номер телефона

    Returns:
        bool: True если номер валиден
    """
    # Убираем все кроме цифр и +
    clean_phone = re.sub(r'[^\d+]', '', phone)

    # Российские форматы
    patterns = [
        r'^\+7\d{10}$',  # +7XXXXXXXXXX
        r'^8\d{10}$',    # 8XXXXXXXXXX
        r'^7\d{10}$',    # 7XXXXXXXXXX
    ]

    return any(re.match(pattern, clean_phone) for pattern in patterns)


def validate_hh_token_format(token: str) -> bool:
    """
    Базовая валидация формата HH.ru токена

    Args:
        token: Токен для проверки

    Returns:
        bool: True если формат похож на HH.ru токен
    """
    if not token or len(token) < 10:
        return False

    # TODO: Добавить более строгую валидацию
    # на основе реального формата HH.ru токенов

    return True


def sanitize_string(value: str, max_length: int = None) -> str:
    """
    Санитизация строкового значения

    Args:
        value: Строка для очистки
        max_length: Максимальная длина

    Returns:
        str: Очищенная строка
    """
    if not isinstance(value, str):
        return ""

    # Убираем лишние пробелы
    cleaned = value.strip()

    # Обрезаем до максимальной длины
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length].strip()

    return cleaned


def validate_score(score: Any) -> bool:
    """
    Валидация оценки (0-100)

    Args:
        score: Оценка для проверки

    Returns:
        bool: True если оценка валидна
    """
    try:
        score_int = int(score)
        return 0 <= score_int <= 100
    except (ValueError, TypeError):
        return False


def validate_recommendation(recommendation: str) -> bool:
    """
    Валидация рекомендации AI

    Args:
        recommendation: Рекомендация для проверки

    Returns:
        bool: True если рекомендация валидна
    """
    valid_recommendations = {"hire", "interview", "maybe", "reject"}
    return recommendation in valid_recommendations


def validate_salary_match(salary_match: str) -> bool:
    """
    Валидация типа соответствия зарплаты

    Args:
        salary_match: Тип соответствия

    Returns:
        bool: True если тип валиден
    """
    valid_types = {"match", "higher", "lower", "unknown"}
    return salary_match in valid_types