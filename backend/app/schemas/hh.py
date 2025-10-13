"""
Pydantic схемы для HH.ru интеграции
Валидация данных вакансий и откликов
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class HHVacancyBasic(BaseModel):
    """Базовая информация о вакансии из HH.ru"""
    hh_vacancy_id: str = Field(..., description="ID вакансии в HH.ru")
    title: str = Field(..., description="Название вакансии")
    applications_count: int = Field(default=0, description="Количество откликов")
    is_active: bool = Field(default=True, description="Активна ли вакансия")

    class Config:
        schema_extra = {
            "example": {
                "hh_vacancy_id": "12345678",
                "title": "Python разработчик",
                "applications_count": 25,
                "is_active": True
            }
        }


class HHVacancyFull(BaseModel):
    """Полная информация о вакансии"""
    id: str = Field(..., description="UUID вакансии в системе")
    hh_vacancy_id: str = Field(..., description="ID вакансии в HH.ru")
    title: str = Field(..., description="Название вакансии")
    description: Optional[str] = Field(None, description="Описание вакансии")
    key_skills: List[str] = Field(default_factory=list, description="Ключевые навыки")

    # Зарплата
    salary_from: Optional[int] = Field(None, description="Зарплата от")
    salary_to: Optional[int] = Field(None, description="Зарплата до")
    currency: str = Field(default="RUB", description="Валюта")

    # Параметры
    experience: Optional[str] = Field(None, description="Требуемый опыт")
    employment: Optional[str] = Field(None, description="Тип занятости")
    schedule: Optional[str] = Field(None, description="График работы")
    area: Optional[str] = Field(None, description="Город")

    # Статистика
    applications_count: int = Field(default=0, description="Всего откликов")
    new_applications_count: int = Field(default=0, description="Новых откликов")
    is_active: bool = Field(default=True, description="Активна ли вакансия")

    # Даты
    published_at: Optional[datetime] = Field(None, description="Дата публикации")
    last_synced_at: Optional[datetime] = Field(None, description="Последняя синхронизация")
    created_at: Optional[datetime] = Field(None, description="Дата создания в системе")

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "hh_vacancy_id": "12345678",
                "title": "Python разработчик",
                "description": "Ищем опытного Python разработчика...",
                "key_skills": ["Python", "Django", "PostgreSQL"],
                "salary_from": 150000,
                "salary_to": 250000,
                "currency": "RUB",
                "experience": "between1And3",
                "employment": "full",
                "schedule": "fullDay",
                "area": "Москва",
                "applications_count": 25,
                "new_applications_count": 5
            }
        }


class HHApplication(BaseModel):
    """Отклик на вакансию из HH.ru"""
    id: str = Field(..., description="UUID отклика в системе")
    vacancy_id: str = Field(..., description="UUID вакансии")
    hh_application_id: str = Field(..., description="ID отклика в HH.ru")
    hh_resume_id: Optional[str] = Field(None, description="ID резюме в HH.ru")

    # Данные кандидата
    candidate_name: Optional[str] = Field(None, description="Имя кандидата")
    candidate_email: Optional[str] = Field(None, description="Email кандидата")
    candidate_phone: Optional[str] = Field(None, description="Телефон кандидата")
    resume_url: Optional[str] = Field(None, description="Ссылка на резюме")

    # Статус
    is_duplicate: bool = Field(default=False, description="Является ли дубликатом")
    analyzed_at: Optional[datetime] = Field(None, description="Время анализа")
    created_at: Optional[datetime] = Field(None, description="Время создания")

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "vacancy_id": "550e8400-e29b-41d4-a716-446655440000",
                "hh_application_id": "app123456",
                "hh_resume_id": "resume789",
                "candidate_name": "Иван Петров",
                "candidate_email": "ivan@example.com",
                "candidate_phone": "+7 (999) 123-45-67",
                "is_duplicate": False
            }
        }


class SyncJobCreate(BaseModel):
    """Создание задачи синхронизации"""
    sync_vacancies: bool = Field(default=True, description="Синхронизировать вакансии")
    sync_applications: bool = Field(default=True, description="Синхронизировать отклики")
    force_full_sync: bool = Field(default=False, description="Полная синхронизация")

    class Config:
        schema_extra = {
            "example": {
                "sync_vacancies": True,
                "sync_applications": True,
                "force_full_sync": False
            }
        }


class SyncJobStatus(BaseModel):
    """Статус задачи синхронизации"""
    id: str = Field(..., description="UUID задачи")
    status: str = Field(..., description="Статус задачи")
    vacancies_synced: int = Field(default=0, description="Синхронизировано вакансий")
    applications_synced: int = Field(default=0, description="Синхронизировано откликов")
    errors: List[str] = Field(default_factory=list, description="Ошибки при синхронизации")

    started_at: Optional[datetime] = Field(None, description="Время начала")
    completed_at: Optional[datetime] = Field(None, description="Время завершения")
    created_at: Optional[datetime] = Field(None, description="Время создания")

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "status": "completed",
                "vacancies_synced": 10,
                "applications_synced": 150,
                "errors": []
            }
        }


class HHTokenValidation(BaseModel):
    """Результат валидации HH.ru токена"""
    is_valid: bool = Field(..., description="Валиден ли токен")
    employer_name: Optional[str] = Field(None, description="Название работодателя")
    error_message: Optional[str] = Field(None, description="Сообщение об ошибке")

    class Config:
        schema_extra = {
            "example": {
                "is_valid": True,
                "employer_name": "ООО Рога и Копыта",
                "error_message": None
            }
        }


class HHTokenCreate(BaseModel):
    """Схема для сохранения HH.ru токена"""
    token: str = Field(..., min_length=10, description="HH.ru API токен")

    @validator('token')
    def validate_token_format(cls, v):
        """Базовая валидация формата токена"""
        if not v or len(v.strip()) < 10:
            raise ValueError("Токен должен содержать минимум 10 символов")

        # Удаляем лишние пробелы
        v = v.strip()

        # Проверяем что токен состоит из допустимых символов
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~')
        if not all(c in allowed_chars for c in v):
            raise ValueError("Токен содержит недопустимые символы")

        return v

    class Config:
        schema_extra = {
            "example": {
                "token": "your_hh_api_token_here"
            }
        }


class HHTokenResponse(BaseModel):
    """Ответ после сохранения токена"""
    success: bool = Field(..., description="Успешно ли сохранен токен")
    token_verified: bool = Field(..., description="Верифицирован ли токен")
    employer_name: Optional[str] = Field(None, description="Название компании")
    message: str = Field(..., description="Сообщение о результате")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "token_verified": True,
                "employer_name": "ООО Рога и Копыта",
                "message": "Токен успешно сохранен и верифицирован"
            }
        }


class HHIntegrationStatus(BaseModel):
    """Статус интеграции с HH.ru"""
    has_token: bool = Field(..., description="Есть ли сохраненный токен")
    token_verified: bool = Field(..., description="Верифицирован ли токен")
    employer_name: Optional[str] = Field(None, description="Название компании")
    token_verified_at: Optional[datetime] = Field(None, description="Дата верификации")
    last_sync_at: Optional[datetime] = Field(None, description="Последняя синхронизация")

    class Config:
        schema_extra = {
            "example": {
                "has_token": True,
                "token_verified": True,
                "employer_name": "ООО Рога и Копыта",
                "token_verified_at": "2024-01-15T10:30:00Z",
                "last_sync_at": "2024-01-15T14:20:00Z"
            }
        }