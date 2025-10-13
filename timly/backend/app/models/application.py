"""
Модель отклика на вакансию
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Application(Base):
    """Модель отклика (заявки) на вакансию"""
    __tablename__ = "applications"
    
    # Первичный ключ
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Связь с вакансией
    vacancy_id = Column(UUID(as_uuid=True), ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False)
    
    # Данные отклика
    hh_application_id = Column(String(50), nullable=False)  # ID отклика на HH.ru
    hh_resume_id = Column(String(50), nullable=True)  # ID резюме на HH.ru
    
    # Информация о кандидате
    candidate_name = Column(String(255), nullable=True)
    candidate_email = Column(String(255), nullable=True)
    candidate_phone = Column(String(50), nullable=True)
    
    # Для дедупликации
    resume_hash = Column(String(64), nullable=True, index=True)  # MD5 хеш резюме
    
    # Результаты анализа AI
    analysis_result = Column(JSON, nullable=True)  # Полный результат анализа
    score = Column(Integer, nullable=True)  # Оценка от 0 до 100
    ai_summary = Column(String, nullable=True)  # Краткое резюме от AI
    
    # Статус обработки
    status = Column(String(50), default="pending")  # pending, analyzing, completed, error
    error_message = Column(String, nullable=True)
    
    # Метаданные
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Ограничения
    __table_args__ = (
        UniqueConstraint('vacancy_id', 'hh_application_id', name='_vacancy_application_uc'),
        CheckConstraint('score >= 0 AND score <= 100', name='score_range_check'),
    )
    
    # Связи
    vacancy = relationship("Vacancy", back_populates="applications")