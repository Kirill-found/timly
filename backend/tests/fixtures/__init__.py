"""
Mock данные для тестирования HH.ru интеграции
Fixtures содержат реалистичные данные российского IT рынка
"""

from .hh_vacancies import (
    MOCK_VACANCIES,
    get_mock_vacancy_by_id,
    get_mock_vacancies_page
)
from .hh_applications import (
    MOCK_APPLICATIONS,
    get_mock_applications_by_vacancy_id,
    get_mock_application_by_id,
    get_mock_resume_by_id
)

__all__ = [
    "MOCK_VACANCIES",
    "MOCK_APPLICATIONS",
    "get_mock_vacancy_by_id",
    "get_mock_vacancies_page",
    "get_mock_applications_by_vacancy_id",
    "get_mock_application_by_id",
    "get_mock_resume_by_id",
]