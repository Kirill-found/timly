"""
Модель поиска по базе резюме
Хранит поисковые проекты и найденных кандидатов
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base, GUID


class SearchStatus(str, enum.Enum):
    """Статус поискового проекта"""
    DRAFT = "draft"           # Черновик - ещё не запускали
    RUNNING = "running"       # Поиск выполняется
    COMPLETED = "completed"   # Поиск завершён
    ANALYZING = "analyzing"   # AI анализ найденных резюме
    DONE = "done"            # Всё готово
    FAILED = "failed"        # Ошибка


class ResumeSearch(Base):
    """
    Модель поискового проекта по базе резюме
    Позволяет сохранять и повторять поиски кандидатов
    """
    __tablename__ = "resume_searches"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Связь с вакансией (опционально, для контекста AI анализа)
    vacancy_id = Column(GUID, ForeignKey("vacancies.id", ondelete="SET NULL"), nullable=True, index=True)

    # Название и описание поиска
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Поисковый запрос
    search_query = Column(String(500), nullable=False)

    # Фильтры поиска (JSON)
    filters = Column(JSON, default=dict, nullable=False)
    # Пример: {
    #   "area": "1",
    #   "experience": "between1And3",
    #   "salary_from": 100000,
    #   "salary_to": 200000,
    #   "age_from": 25,
    #   "age_to": 45,
    #   "education_level": "higher"
    # }

    # Статус и статистика
    status = Column(SQLEnum(SearchStatus), default=SearchStatus.DRAFT, nullable=False, index=True)
    total_found = Column(Integer, default=0, nullable=False)  # Всего найдено в HH
    processed_count = Column(Integer, default=0, nullable=False)  # Обработано/загружено
    analyzed_count = Column(Integer, default=0, nullable=False)  # Проанализировано AI

    # Ошибки
    error_message = Column(Text, nullable=True)

    # Метаданные
    last_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Отношения
    user = relationship("User", backref="resume_searches")
    vacancy = relationship("Vacancy", backref="resume_searches")
    candidates = relationship("SearchCandidate", back_populates="search", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ResumeSearch(id={self.id}, name={self.name}, status={self.status})>"

    def to_dict(self):
        """Сериализация для API"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "vacancy_id": str(self.vacancy_id) if self.vacancy_id else None,
            "name": self.name,
            "description": self.description,
            "search_query": self.search_query,
            "filters": self.filters,
            "status": self.status.value,
            "total_found": self.total_found,
            "processed_count": self.processed_count,
            "analyzed_count": self.analyzed_count,
            "error_message": self.error_message,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SearchCandidate(Base):
    """
    Модель найденного кандидата из поиска
    Хранит данные резюме и результаты AI анализа
    """
    __tablename__ = "search_candidates"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    search_id = Column(GUID, ForeignKey("resume_searches.id", ondelete="CASCADE"), nullable=False, index=True)

    # Данные из HH.ru
    hh_resume_id = Column(String(100), nullable=False, index=True)

    # Основная информация
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    middle_name = Column(String(100), nullable=True)
    title = Column(String(255), nullable=True)  # Желаемая должность
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    area = Column(String(255), nullable=True)  # Город

    # Профессиональные данные
    salary = Column(Integer, nullable=True)  # Желаемая зарплата
    currency = Column(String(3), default="RUB")
    experience_years = Column(Integer, nullable=True)  # Общий стаж в месяцах
    skills = Column(JSON, default=list)  # Ключевые навыки

    # Полные данные резюме (JSON)
    resume_data = Column(JSON, default=dict, nullable=False)

    # AI Анализ
    is_analyzed = Column(Boolean, default=False, nullable=False, index=True)
    ai_score = Column(Integer, nullable=True)  # 0-100
    ai_recommendation = Column(String(50), nullable=True)  # hire, consider, reject
    ai_summary = Column(Text, nullable=True)  # Краткое резюме от AI
    ai_strengths = Column(JSON, default=list)  # Сильные стороны
    ai_weaknesses = Column(JSON, default=list)  # Слабые стороны
    ai_analysis_data = Column(JSON, default=dict)  # Полный анализ
    analyzed_at = Column(DateTime, nullable=True)

    # Статус работы с кандидатом
    is_favorite = Column(Boolean, default=False, nullable=False)
    is_contacted = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)  # Заметки рекрутера

    # Метаданные
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Отношения
    search = relationship("ResumeSearch", back_populates="candidates")

    def __repr__(self):
        return f"<SearchCandidate(id={self.id}, name={self.first_name} {self.last_name}, score={self.ai_score})>"

    @property
    def full_name(self) -> str:
        """Полное имя кандидата"""
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(filter(None, parts)) or "Имя не указано"

    def to_dict(self):
        """Сериализация для API"""
        return {
            "id": str(self.id),
            "search_id": str(self.search_id),
            "hh_resume_id": self.hh_resume_id,
            "full_name": self.full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "title": self.title,
            "age": self.age,
            "gender": self.gender,
            "area": self.area,
            "salary": self.salary,
            "currency": self.currency,
            "experience_years": self.experience_years,
            "skills": self.skills,
            # AI анализ
            "is_analyzed": self.is_analyzed,
            "ai_score": self.ai_score,
            "ai_recommendation": self.ai_recommendation,
            "ai_summary": self.ai_summary,
            "ai_strengths": self.ai_strengths,
            "ai_weaknesses": self.ai_weaknesses,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            # Статус
            "is_favorite": self.is_favorite,
            "is_contacted": self.is_contacted,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_dict_full(self):
        """Полная сериализация с данными резюме"""
        data = self.to_dict()
        data["resume_data"] = self.resume_data
        data["ai_analysis_data"] = self.ai_analysis_data
        return data
