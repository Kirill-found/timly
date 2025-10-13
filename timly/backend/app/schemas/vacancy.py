"""
Pydantic схемы для вакансий
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, UUID4


class VacancyBase(BaseModel):
    """Базовая схема вакансии"""
    title: str
    company_name: Optional[str] = None


class VacancyCreate(VacancyBase):
    """Схема для создания вакансии"""
    hh_vacancy_id: str


class VacancyResponse(VacancyBase):
    """Схема ответа с данными вакансии"""
    id: UUID4
    hh_vacancy_id: str
    last_synced_at: Optional[datetime]
    created_at: datetime
    applications_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class VacancySyncRequest(BaseModel):
    """Запрос на синхронизацию вакансий"""
    force_update: bool = Field(False, description="Принудительное обновление всех вакансий")


class ApplicationBase(BaseModel):
    """Базовая схема отклика"""
    candidate_name: Optional[str]
    candidate_email: Optional[str]
    candidate_phone: Optional[str]


class ApplicationResponse(ApplicationBase):
    """Схема ответа с данными отклика"""
    id: UUID4
    hh_application_id: str
    hh_resume_id: Optional[str]
    score: Optional[int]
    ai_summary: Optional[str]
    status: str
    processed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    """Запрос на анализ откликов"""
    vacancy_id: UUID4
    analyze_all: bool = Field(False, description="Анализировать все отклики, включая обработанные")


class AnalysisResult(BaseModel):
    """Результат анализа отклика"""
    application_id: UUID4
    score: int = Field(..., ge=0, le=100, description="Оценка соответствия от 0 до 100")
    summary: str = Field(..., description="Краткое резюме анализа")
    strengths: List[str] = Field(default_factory=list, description="Сильные стороны кандидата")
    weaknesses: List[str] = Field(default_factory=list, description="Слабые стороны кандидата")
    recommendation: str = Field(..., description="Рекомендация по кандидату")
    detailed_analysis: Dict[str, Any] = Field(default_factory=dict, description="Детальный анализ")