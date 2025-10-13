"""
Модели базы данных
"""
from app.models.user import User
from app.models.vacancy import Vacancy
from app.models.application import Application

__all__ = ["User", "Vacancy", "Application"]