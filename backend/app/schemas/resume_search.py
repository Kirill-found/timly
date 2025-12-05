"""
Схемы для поиска по базе резюме
Валидация запросов и ответов API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SearchStatusEnum(str, Enum):
    """Статус поискового проекта"""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    ANALYZING = "analyzing"
    DONE = "done"
    FAILED = "failed"


# ==================== Фильтры поиска ====================

class SearchFilters(BaseModel):
    """Фильтры для поиска резюме"""
    area: Optional[str] = Field(None, description="ID региона (1 - Москва, 2 - СПб)")
    experience: Optional[str] = Field(None, description="Опыт: noExperience, between1And3, between3And6, moreThan6")
    salary_from: Optional[int] = Field(None, ge=0, description="Минимальная зарплата")
    salary_to: Optional[int] = Field(None, ge=0, description="Максимальная зарплата")
    age_from: Optional[int] = Field(None, ge=18, le=70, description="Минимальный возраст")
    age_to: Optional[int] = Field(None, ge=18, le=70, description="Максимальный возраст")
    gender: Optional[str] = Field(None, description="Пол: male, female")
    education_level: Optional[str] = Field(None, description="Образование: higher, bachelor, master и т.д.")
    job_search_status: Optional[str] = Field(None, description="Статус поиска: active, passive")
    relocation: Optional[str] = Field(None, description="Готовность к переезду")

    class Config:
        json_schema_extra = {
            "example": {
                "area": "1",
                "experience": "between1And3",
                "salary_from": 100000,
                "salary_to": 200000
            }
        }


# ==================== Создание поиска ====================

class ResumeSearchCreate(BaseModel):
    """Создание нового поискового проекта"""
    name: str = Field(..., min_length=1, max_length=255, description="Название поиска")
    description: Optional[str] = Field(None, max_length=1000, description="Описание")
    search_query: str = Field(..., min_length=1, max_length=500, description="Поисковый запрос")
    vacancy_id: Optional[str] = Field(None, description="ID вакансии для контекста анализа")
    filters: Optional[SearchFilters] = Field(default_factory=SearchFilters, description="Фильтры поиска")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Python разработчики в Москве",
                "description": "Поиск Senior Python разработчиков",
                "search_query": "Python Django FastAPI",
                "vacancy_id": None,
                "filters": {
                    "area": "1",
                    "experience": "between3And6",
                    "salary_from": 200000
                }
            }
        }


class ResumeSearchUpdate(BaseModel):
    """Обновление поискового проекта"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    search_query: Optional[str] = Field(None, min_length=1, max_length=500)
    vacancy_id: Optional[str] = None
    filters: Optional[SearchFilters] = None


# ==================== Ответы ====================

class ResumeSearchResponse(BaseModel):
    """Данные поискового проекта"""
    id: str
    user_id: str
    vacancy_id: Optional[str]
    name: str
    description: Optional[str]
    search_query: str
    filters: Dict[str, Any]
    status: SearchStatusEnum
    total_found: int
    processed_count: int
    analyzed_count: int
    error_message: Optional[str]
    last_run_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateResponse(BaseModel):
    """Данные найденного кандидата"""
    id: str
    search_id: str
    hh_resume_id: str
    full_name: str
    first_name: Optional[str]
    last_name: Optional[str]
    title: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    area: Optional[str]
    salary: Optional[int]
    currency: str
    experience_years: Optional[int]
    skills: List[str]
    # AI анализ
    is_analyzed: bool
    ai_score: Optional[int]
    ai_recommendation: Optional[str]
    ai_summary: Optional[str]
    ai_strengths: List[str]
    ai_weaknesses: List[str]
    analyzed_at: Optional[datetime]
    # Статус
    is_favorite: bool
    is_contacted: bool
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateDetailResponse(CandidateResponse):
    """Полные данные кандидата с резюме"""
    resume_data: Dict[str, Any]
    ai_analysis_data: Dict[str, Any]


# ==================== Списки ====================

class ResumeSearchListResponse(BaseModel):
    """Список поисковых проектов"""
    searches: List[ResumeSearchResponse]
    total: int


class CandidateListResponse(BaseModel):
    """Список кандидатов"""
    candidates: List[CandidateResponse]
    total: int
    page: int
    per_page: int


# ==================== Действия ====================

class RunSearchRequest(BaseModel):
    """Запуск поиска"""
    max_results: int = Field(default=100, ge=1, le=500, description="Максимум результатов для загрузки")


class AnalyzeCandidatesRequest(BaseModel):
    """Запуск AI анализа кандидатов"""
    candidate_ids: Optional[List[str]] = Field(None, description="ID кандидатов для анализа (все, если не указано)")
    force_reanalysis: bool = Field(default=False, description="Переанализировать уже проанализированных")


class UpdateCandidateRequest(BaseModel):
    """Обновление данных кандидата"""
    is_favorite: Optional[bool] = None
    is_contacted: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=5000)


# ==================== Справочники ====================

class DictionaryItem(BaseModel):
    """Элемент справочника"""
    id: str
    name: str


class AreaItem(BaseModel):
    """Регион"""
    id: str
    name: str
    parent_id: Optional[str] = None


class SearchDictionaries(BaseModel):
    """Справочники для фильтров поиска"""
    experience: List[DictionaryItem]
    education_level: List[DictionaryItem]
    gender: List[DictionaryItem]
    job_search_status: List[DictionaryItem]
    relocation: List[DictionaryItem]
    order_by: List[DictionaryItem]
    areas: List[AreaItem]


# ==================== Статистика ====================

class SearchStats(BaseModel):
    """Статистика по поиску"""
    total_candidates: int
    analyzed_count: int
    hire_count: int  # Рекомендация "нанять"
    consider_count: int  # Рекомендация "рассмотреть"
    reject_count: int  # Рекомендация "отклонить"
    favorites_count: int
    contacted_count: int
    avg_score: Optional[float]
