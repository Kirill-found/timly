"""
Модель вакансии
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Vacancy(Base):
    """Модель вакансии с HH.ru"""
    __tablename__ = "vacancies"
    
    # Первичный ключ
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Связь с пользователем
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Данные вакансии
    hh_vacancy_id = Column(String(50), nullable=False)  # ID вакансии на HH.ru
    title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=True)
    
    # Сырые данные с HH.ru (JSON)
    raw_data = Column(JSON, nullable=True)
    
    # Метаданные
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Уникальность: одна вакансия на пользователя
    __table_args__ = (
        UniqueConstraint('user_id', 'hh_vacancy_id', name='_user_vacancy_uc'),
    )
    
    # Связи
    user = relationship("User", backref="vacancies")
    applications = relationship("Application", back_populates="vacancy", cascade="all, delete-orphan")