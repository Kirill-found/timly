"""
Модель загруженных кандидатов
Хранит резюме, загруженные пользователем из PDF/Excel
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base, GUID


class UploadSource(str, enum.Enum):
    """Источник загрузки резюме"""
    PDF = "pdf"
    EXCEL = "excel"
    MANUAL = "manual"  # Ручной ввод


class UploadedCandidate(Base):
    """
    Модель загруженного кандидата
    Резюме, загруженные пользователем из файлов (PDF, Excel)
    """
    __tablename__ = "uploaded_candidates"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Связь с вакансией для AI анализа
    vacancy_id = Column(GUID, ForeignKey("vacancies.id", ondelete="SET NULL"), nullable=True, index=True)

    # Источник данных
    source = Column(SQLEnum(UploadSource), default=UploadSource.PDF, nullable=False)
    original_filename = Column(String(500), nullable=True)  # Имя исходного файла
    original_text = Column(Text, nullable=True)  # Сырой текст из PDF

    # Основная информация (извлечённая AI или из Excel)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    middle_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)

    # Профессиональные данные
    title = Column(String(255), nullable=True)  # Желаемая должность
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    city = Column(String(255), nullable=True)

    salary_expectation = Column(Integer, nullable=True)
    currency = Column(String(3), default="RUB")
    experience_years = Column(Integer, nullable=True)
    experience_text = Column(Text, nullable=True)  # Описание опыта работы

    skills = Column(JSON, default=list)  # Ключевые навыки
    education = Column(Text, nullable=True)

    # Полные данные (структурированные AI)
    parsed_data = Column(JSON, default=dict, nullable=False)

    # AI Анализ
    is_analyzed = Column(Boolean, default=False, nullable=False, index=True)
    ai_score = Column(Integer, nullable=True)  # 0-100
    ai_recommendation = Column(String(50), nullable=True)  # hire, interview, maybe, reject
    ai_summary = Column(Text, nullable=True)
    ai_strengths = Column(JSON, default=list)
    ai_weaknesses = Column(JSON, default=list)
    ai_red_flags = Column(JSON, default=list)
    ai_analysis_data = Column(JSON, default=dict)
    analyzed_at = Column(DateTime, nullable=True)

    # Статус работы с кандидатом
    is_favorite = Column(Boolean, default=False, nullable=False)
    is_contacted = Column(Boolean, default=False, nullable=False)
    contact_status = Column(String(50), nullable=True)  # pending, contacted, interviewed, rejected, hired
    notes = Column(Text, nullable=True)

    # Метаданные
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Отношения
    user = relationship("User", backref="uploaded_candidates")
    vacancy = relationship("Vacancy", backref="uploaded_candidates")

    def __repr__(self):
        return f"<UploadedCandidate(id={self.id}, name={self.full_name}, score={self.ai_score})>"

    @property
    def full_name(self) -> str:
        """Полное имя кандидата"""
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(filter(None, parts)) or "Имя не указано"

    def to_dict(self):
        """Сериализация для API"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "vacancy_id": str(self.vacancy_id) if self.vacancy_id else None,
            "source": self.source.value,
            "original_filename": self.original_filename,
            "full_name": self.full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "title": self.title,
            "age": self.age,
            "city": self.city,
            "salary_expectation": self.salary_expectation,
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
            "ai_red_flags": self.ai_red_flags,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            # Статус
            "is_favorite": self.is_favorite,
            "is_contacted": self.is_contacted,
            "contact_status": self.contact_status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_dict_full(self):
        """Полная сериализация с сырыми данными"""
        data = self.to_dict()
        data["original_text"] = self.original_text
        data["experience_text"] = self.experience_text
        data["education"] = self.education
        data["parsed_data"] = self.parsed_data
        data["ai_analysis_data"] = self.ai_analysis_data
        return data
