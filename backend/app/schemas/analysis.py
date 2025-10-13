"""
Pydantic схемы для AI анализа резюме
Валидация результатов анализа и запросов на анализ
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class AnalysisRequest(BaseModel):
    """Запрос на анализ резюме"""
    application_ids: List[str] = Field(..., min_items=1, max_items=5, description="Список ID откликов для анализа (макс. 5)")
    force_reanalysis: bool = Field(default=False, description="Переанализировать уже обработанные")

    @validator('application_ids')
    def validate_application_ids(cls, v):
        """Валидация UUID формата"""
        if len(v) > 5:
            raise ValueError('Максимум 5 откликов за раз для оптимизации стоимости')
        return v

    class Config:
        schema_extra = {
            "example": {
                "application_ids": [
                    "550e8400-e29b-41d4-a716-446655440001",
                    "550e8400-e29b-41d4-a716-446655440002"
                ],
                "force_reanalysis": False
            }
        }


class AnalysisResult(BaseModel):
    """Результат AI анализа резюме"""
    id: str = Field(..., description="UUID результата анализа")
    application_id: str = Field(..., description="UUID отклика")

    # Основные оценки (0-100)
    score: Optional[int] = Field(None, ge=0, le=100, description="Общая оценка кандидата")
    skills_match: Optional[int] = Field(None, ge=0, le=100, description="Соответствие навыков")
    experience_match: Optional[int] = Field(None, ge=0, le=100, description="Соответствие опыта")
    salary_match: Optional[str] = Field(None, description="Соответствие зарплаты")

    # Детальный анализ
    strengths: List[str] = Field(default_factory=list, description="Сильные стороны кандидата")
    weaknesses: List[str] = Field(default_factory=list, description="Слабые стороны")
    red_flags: List[str] = Field(default_factory=list, description="Красные флаги")
    recommendation: Optional[str] = Field(None, description="Рекомендация: hire/interview/maybe/reject")
    reasoning: Optional[str] = Field(None, description="Обоснование оценки")

    # Метаданные
    ai_model: Optional[str] = Field(None, description="Использованная AI модель")
    ai_tokens_used: Optional[int] = Field(None, description="Потрачено токенов")
    ai_cost_cents: Optional[int] = Field(None, description="Стоимость в копейках")
    processing_time_ms: Optional[int] = Field(None, description="Время обработки в мс")
    created_at: Optional[datetime] = Field(None, description="Время создания анализа")

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440003",
                "application_id": "550e8400-e29b-41d4-a716-446655440001",
                "score": 85,
                "skills_match": 90,
                "experience_match": 80,
                "salary_match": "match",
                "strengths": [
                    "5+ лет опыта работы с Python",
                    "Опыт работы с Django и FastAPI",
                    "Знание Docker и CI/CD"
                ],
                "weaknesses": [
                    "Нет опыта работы с Kubernetes",
                    "Слабые знания фронтенда"
                ],
                "red_flags": [],
                "recommendation": "interview",
                "reasoning": "Кандидат имеет сильные технические навыки и подходящий опыт. Рекомендуется техническое собеседование.",
                "ai_model": "gpt-4o-mini",
                "ai_tokens_used": 1250,
                "ai_cost_cents": 15,
                "processing_time_ms": 2300
            }
        }


class BatchAnalysisResponse(BaseModel):
    """Ответ на запрос пакетного анализа"""
    job_id: str = Field(..., description="ID фоновой задачи")
    message: str = Field(..., description="Сообщение о статусе")
    applications_queued: int = Field(..., description="Количество откликов в очереди")
    estimated_time_seconds: int = Field(..., description="Примерное время выполнения")

    class Config:
        schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440004",
                "message": "Анализ поставлен в очередь",
                "applications_queued": 3,
                "estimated_time_seconds": 45
            }
        }


class AnalysisFilter(BaseModel):
    """Фильтры для получения результатов анализа"""
    vacancy_id: Optional[str] = Field(None, description="Фильтр по вакансии")
    min_score: Optional[int] = Field(None, ge=0, le=100, description="Минимальная оценка")
    max_score: Optional[int] = Field(None, ge=0, le=100, description="Максимальная оценка")
    recommendation: Optional[str] = Field(None, description="Фильтр по рекомендации")
    has_red_flags: Optional[bool] = Field(None, description="Есть ли красные флаги")
    analyzed_after: Optional[datetime] = Field(None, description="Анализированы после даты")
    limit: int = Field(default=50, le=200, description="Количество результатов")
    offset: int = Field(default=0, ge=0, description="Смещение для пагинации")

    @validator('max_score')
    def validate_score_range(cls, v, values):
        """Проверка диапазона оценок"""
        min_score = values.get('min_score')
        if min_score is not None and v is not None and v < min_score:
            raise ValueError('max_score должен быть больше min_score')
        return v

    class Config:
        schema_extra = {
            "example": {
                "vacancy_id": "550e8400-e29b-41d4-a716-446655440000",
                "min_score": 70,
                "recommendation": "interview",
                "limit": 20
            }
        }


class AnalysisStats(BaseModel):
    """Статистика анализа по вакансии"""
    vacancy_id: str = Field(..., description="UUID вакансии")
    total_applications: int = Field(..., description="Всего откликов")
    analyzed_applications: int = Field(..., description="Проанализировано откликов")
    avg_score: Optional[float] = Field(None, description="Средняя оценка")

    # Распределение по рекомендациям
    hire_count: int = Field(default=0, description="Рекомендованы к найму")
    interview_count: int = Field(default=0, description="Рекомендованы к собеседованию")
    maybe_count: int = Field(default=0, description="Возможно подходят")
    reject_count: int = Field(default=0, description="Рекомендованы к отклонению")

    # Метаданные
    last_analysis_at: Optional[datetime] = Field(None, description="Последний анализ")
    total_ai_cost_cents: Optional[int] = Field(None, description="Общая стоимость анализа")

    class Config:
        schema_extra = {
            "example": {
                "vacancy_id": "550e8400-e29b-41d4-a716-446655440000",
                "total_applications": 50,
                "analyzed_applications": 45,
                "avg_score": 72.5,
                "hire_count": 3,
                "interview_count": 12,
                "maybe_count": 20,
                "reject_count": 10,
                "total_ai_cost_cents": 750
            }
        }


class ExportRequest(BaseModel):
    """Запрос на экспорт результатов в Excel"""
    vacancy_id: str = Field(..., description="UUID вакансии для экспорта")
    include_resume_data: bool = Field(default=False, description="Включать данные резюме")
    min_score: Optional[int] = Field(None, ge=0, le=100, description="Минимальная оценка")
    recommendation: Optional[str] = Field(None, description="Фильтр по рекомендации")

    class Config:
        schema_extra = {
            "example": {
                "vacancy_id": "550e8400-e29b-41d4-a716-446655440000",
                "include_resume_data": False,
                "min_score": 70
            }
        }