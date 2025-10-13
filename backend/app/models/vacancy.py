"""
Модель вакансии из HH.ru
Хранит данные вакансий и связанную статистику
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base, GUID


class Vacancy(Base):
    """
    Модель вакансии, синхронизированной с HH.ru
    Связана с пользователем и содержит статистику откликов
    """
    __tablename__ = "vacancies"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Данные из HH.ru API
    hh_vacancy_id = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    key_skills = Column(JSON, default=list, nullable=False)  # Навыки из HH.ru

    # Параметры вакансии
    salary_from = Column(Integer, nullable=True)
    salary_to = Column(Integer, nullable=True)
    currency = Column(String(3), default="RUB")
    experience = Column(String(50), nullable=True)  # "noExperience", "between1And3", etc.
    employment = Column(String(50), nullable=True)  # "full", "part", etc.
    schedule = Column(String(50), nullable=True)    # "fullDay", "remote", etc.
    area = Column(String(255), nullable=True)       # Город

    # Статус и статистика
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    published_at = Column(DateTime, nullable=True)
    applications_count = Column(Integer, default=0, nullable=False)
    new_applications_count = Column(Integer, default=0, nullable=False)
    last_synced_at = Column(DateTime, nullable=True)

    # Метаданные
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Отношения
    user = relationship("User", backref="vacancies")
    applications = relationship("Application", back_populates="vacancy", cascade="all, delete-orphan")

    # Составной UNIQUE constraint для уникальности (user_id, hh_vacancy_id)
    __table_args__ = (
        UniqueConstraint('user_id', 'hh_vacancy_id', name='uq_user_vacancy'),
    )

    def __repr__(self):
        return f"<Vacancy(id={self.id}, title={self.title}, hh_id={self.hh_vacancy_id})>"

    def to_dict(self):
        """Сериализация для API"""
        return {
            "id": str(self.id),
            "hh_vacancy_id": self.hh_vacancy_id,
            "title": self.title,
            "description": self.description,
            "key_skills": self.key_skills,
            "salary": {
                "from": self.salary_from,
                "to": self.salary_to,
                "currency": self.currency
            },
            "experience": self.experience,
            "employment": self.employment,
            "schedule": self.schedule,
            "area": self.area,
            "is_active": self.is_active,
            "applications_count": self.applications_count,
            "new_applications_count": self.new_applications_count,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @property
    def salary_text(self) -> str:
        """Текстовое представление зарплаты"""
        if not self.salary_from and not self.salary_to:
            return "Не указана"
        elif self.salary_from and self.salary_to:
            return f"{self.salary_from:,} - {self.salary_to:,} {self.currency}"
        elif self.salary_from:
            return f"от {self.salary_from:,} {self.currency}"
        else:
            return f"до {self.salary_to:,} {self.currency}"