"""
Модели заявок на вакансии и результатов анализа
Отклики кандидатов и AI анализ резюме
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, CheckConstraint, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base, GUID


class RecommendationType(enum.Enum):
    """Рекомендации по кандидату"""
    hire = "hire"           # Нанимать
    interview = "interview" # Пригласить на собеседование
    maybe = "maybe"         # Возможно подходит
    reject = "reject"       # Отклонить


class JobStatus(enum.Enum):
    """Статусы фоновых задач"""
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Application(Base):
    """
    Модель отклика на вакансию
    Содержит данные резюме и связана с результатами анализа
    """
    __tablename__ = "applications"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    vacancy_id = Column(GUID, ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False, index=True)

    # Идентификаторы из HH.ru
    hh_application_id = Column(String(50), unique=True, nullable=False, index=True)
    hh_resume_id = Column(String(50), nullable=True, index=True)
    hh_negotiation_id = Column(String(50), nullable=True)

    # Данные кандидата
    candidate_name = Column(String(255), nullable=True, index=True)  # Поиск по имени
    candidate_email = Column(String(255), nullable=True)
    candidate_phone = Column(String(50), nullable=True)
    resume_url = Column(String(500), nullable=True)

    # Данные резюме (полная структура из HH.ru)
    resume_data = Column(JSON, nullable=True)
    resume_hash = Column(String(64), nullable=True, index=True)  # MD5 для дедупликации

    # Статусы и коллекции из HH.ru (для фильтрации)
    collection_id = Column(String(50), nullable=True, index=True)  # response, consider, interview, discard
    state = Column(String(50), nullable=True, index=True)          # ID статуса отклика

    # Статус обработки
    is_duplicate = Column(Boolean, default=False, nullable=False, index=True)
    analyzed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Отношения
    vacancy = relationship("Vacancy", back_populates="applications")
    analysis_result = relationship("AnalysisResult", back_populates="application", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Application(id={self.id}, candidate={self.candidate_name}, vacancy_id={self.vacancy_id})>"

    def to_dict(self):
        """Сериализация для API"""
        return {
            "id": str(self.id),
            "vacancy_id": str(self.vacancy_id),
            "hh_application_id": self.hh_application_id,
            "hh_resume_id": self.hh_resume_id,
            "candidate_name": self.candidate_name,
            "candidate_email": self.candidate_email,
            "candidate_phone": self.candidate_phone,
            "resume_url": self.resume_url,
            "collection_id": self.collection_id,
            "state": self.state,
            "is_duplicate": self.is_duplicate,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AnalysisResult(Base):
    """
    Результаты AI анализа резюме
    Отдельная таблица для производительности и масштабируемости
    """
    __tablename__ = "analysis_results"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    application_id = Column(GUID, ForeignKey("applications.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Основные оценки (0-100)
    score = Column(Integer, CheckConstraint("score >= 0 AND score <= 100"), nullable=True, index=True)
    skills_match = Column(Integer, CheckConstraint("skills_match >= 0 AND skills_match <= 100"), nullable=True)
    experience_match = Column(Integer, CheckConstraint("experience_match >= 0 AND experience_match <= 100"), nullable=True)
    salary_match = Column(String(20), nullable=True)  # "match", "higher", "lower", "unknown"

    # Детальный анализ (JSON массивы строк)
    strengths = Column(JSON, nullable=True)      # Сильные стороны
    weaknesses = Column(JSON, nullable=True)     # Слабые стороны
    red_flags = Column(JSON, nullable=True)      # Красные флаги
    recommendation = Column(String(20), nullable=True, index=True)  # hire/interview/maybe/reject
    reasoning = Column(Text, nullable=True)             # Обоснование оценки

    # Метаданные AI анализа
    ai_model = Column(String(50), nullable=True)        # Использованная модель
    ai_tokens_used = Column(Integer, nullable=True)     # Потрачено токенов
    ai_cost_rub = Column(Numeric(6, 2), nullable=True)  # Стоимость в рублях (DECIMAL(6,2))
    processing_time_ms = Column(Integer, nullable=True) # Время обработки

    # Полный JSON ответ AI для дополнительных полей (v3.0)
    raw_result = Column(JSON, nullable=True)  # summary_one_line, experience_years, etc.
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Отношения
    application = relationship("Application", back_populates="analysis_result")

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, score={self.score}, recommendation={self.recommendation})>"

    def to_dict(self):
        """Сериализация для API (v2 - с композитным скорингом)"""
        return {
            "id": str(self.id),
            "application_id": str(self.application_id),
            "score": self.score,
            "skills_match": self.skills_match,
            "experience_match": self.experience_match,
            "salary_match": self.salary_match,
            "strengths": self.strengths or [],
            "weaknesses": self.weaknesses or [],
            "red_flags": self.red_flags or [],
            "recommendation": self.recommendation,
            "reasoning": self.reasoning,
            "ai_model": self.ai_model,
            "ai_tokens_used": self.ai_tokens_used,
            "ai_cost_rub": float(self.ai_cost_rub) if self.ai_cost_rub else None,
            "processing_time_ms": self.processing_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # v2: Полный ответ AI с tier, scores, confidence, interview_questions
            "raw_result": self.raw_result,
        }


class SyncJob(Base):
    """
    Задачи синхронизации с HH.ru
    Отслеживание фоновых задач по получению данных
    """
    __tablename__ = "sync_jobs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    status = Column(String(20), default="pending", nullable=False, index=True)
    vacancies_synced = Column(Integer, default=0, nullable=False)
    applications_synced = Column(Integer, default=0, nullable=False)
    errors = Column(JSON, default=list, nullable=False)  # Список ошибок

    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Отношения
    user = relationship("User", backref="sync_jobs")

    def __repr__(self):
        return f"<SyncJob(id={self.id}, status={self.status}, user_id={self.user_id})>"

    def to_dict(self):
        """Сериализация для API"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "status": self.status,
            "vacancies_synced": self.vacancies_synced,
            "applications_synced": self.applications_synced,
            "errors": self.errors,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }