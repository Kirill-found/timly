"""
Пользовательские исключения для Timly
Типизированные ошибки для разных компонентов системы
"""


class TimlyBaseException(Exception):
    """Базовое исключение для всех ошибок Timly"""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(TimlyBaseException):
    """Ошибки валидации данных"""
    pass


class AuthenticationError(TimlyBaseException):
    """Ошибки аутентификации и авторизации"""
    pass


class HHIntegrationError(TimlyBaseException):
    """Ошибки интеграции с HH.ru API"""

    def __init__(self, message: str, status_code: int = None, details: dict = None):
        self.status_code = status_code
        super().__init__(message, details)


class AIAnalysisError(TimlyBaseException):
    """Ошибки AI анализа резюме"""
    pass


class DatabaseError(TimlyBaseException):
    """Ошибки работы с базой данных"""
    pass


class CacheError(TimlyBaseException):
    """Ошибки работы с кешем Redis"""
    pass


class BackgroundJobError(TimlyBaseException):
    """Ошибки фоновых задач RQ"""

    def __init__(self, message: str, job_id: str = None, details: dict = None):
        self.job_id = job_id
        super().__init__(message, details)

class FileParseError(TimlyBaseException):
    """Ошибки парсинга файлов (PDF, Excel)"""
    pass
