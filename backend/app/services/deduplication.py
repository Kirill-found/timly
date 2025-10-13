"""
Сервис дедупликации резюме
Предотвращение повторного анализа одинаковых резюме
"""
import hashlib
import json
from typing import Dict, Any, Optional, List
import logging
from sqlalchemy.orm import Session

from app.models.application import Application

logger = logging.getLogger(__name__)


class DeduplicationService:
    """
    Сервис для предотвращения дублирования резюме
    Использует MD5 хеширование ключевых полей резюме
    """

    def __init__(self, db: Session):
        self.db = db

    def get_resume_hash(self, resume_data: Dict[str, Any]) -> str:
        """
        Создание стабильного хеша резюме для дедупликации

        Args:
            resume_data: Данные резюме из HH.ru

        Returns:
            str: MD5 хеш ключевых полей
        """
        # Ключевые поля для определения уникальности резюме
        key_fields = [
            # Основная информация
            str(resume_data.get("id", "")),
            resume_data.get("title", "").lower().strip(),
            resume_data.get("first_name", "").lower().strip(),
            resume_data.get("last_name", "").lower().strip(),
            resume_data.get("middle_name", "").lower().strip(),
            str(resume_data.get("age", "")),

            # Контакты
            resume_data.get("contact", [{}])[0].get("value", "") if resume_data.get("contact") else "",

            # Опыт работы (последние 2 места)
            json.dumps([
                {
                    "company": exp.get("company", "").lower().strip(),
                    "position": exp.get("position", "").lower().strip(),
                    "start": exp.get("start", ""),
                    "end": exp.get("end", "")
                }
                for exp in (resume_data.get("experience", []) or [])[:2]
            ], sort_keys=True),

            # Навыки (топ-10)
            json.dumps(sorted([
                skill.get("name", "").lower().strip()
                for skill in (resume_data.get("skill_set", []) or [])
            ])[:10])
        ]

        # Создание стабильного хеша
        hash_string = "|".join(str(field) for field in key_fields)
        return hashlib.md5(hash_string.encode('utf-8')).hexdigest()

    def is_duplicate(self, resume_hash: str, vacancy_id: str) -> Optional[Application]:
        """
        Проверка наличия дубликата резюме для вакансии

        Args:
            resume_hash: Хеш резюме
            vacancy_id: ID вакансии

        Returns:
            Application: Существующая заявка-дубликат или None
        """
        existing_application = self.db.query(Application).filter(
            Application.vacancy_id == vacancy_id,
            Application.resume_hash == resume_hash,
            Application.is_duplicate == False  # Исключаем уже помеченные как дубли
        ).first()

        return existing_application

    def mark_as_duplicate(
        self,
        application_id: str,
        original_application_id: str
    ) -> bool:
        """
        Пометить заявку как дубликат

        Args:
            application_id: ID заявки-дубликата
            original_application_id: ID оригинальной заявки

        Returns:
            bool: Успех операции
        """
        try:
            application = self.db.query(Application).filter(
                Application.id == application_id
            ).first()

            if not application:
                logger.error(f"Заявка {application_id} не найдена")
                return False

            application.is_duplicate = True
            # TODO: Добавить поле original_application_id в модель
            # application.original_application_id = original_application_id

            self.db.commit()

            logger.info(f"Заявка {application_id} помечена как дубликат {original_application_id}")
            return True

        except Exception as e:
            logger.error(f"Ошибка пометки дубликата {application_id}: {e}")
            self.db.rollback()
            return False

    def find_potential_duplicates(
        self,
        vacancy_id: str,
        similarity_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Поиск потенциальных дубликатов среди заявок

        Args:
            vacancy_id: ID вакансии
            similarity_threshold: Порог схожести (0.0-1.0)

        Returns:
            List: Группы потенциальных дубликатов
        """
        # TODO: Реализовать алгоритм поиска потенциальных дубликатов
        # на основе схожести имен, контактов и опыта работы

        applications = self.db.query(Application).filter(
            Application.vacancy_id == vacancy_id,
            Application.is_duplicate == False
        ).all()

        potential_duplicates = []

        # Пока возвращаем заглушку
        return potential_duplicates

    def get_deduplication_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Статистика дедупликации для пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Dict: Статистика дубликатов
        """
        # TODO: Реализовать подсчет статистики дубликатов
        return {
            "total_applications": 245,
            "unique_applications": 198,
            "duplicate_applications": 47,
            "duplicate_rate": 0.19,
            "duplicates_by_vacancy": [
                {
                    "vacancy_id": "550e8400-e29b-41d4-a716-446655440000",
                    "vacancy_title": "Python разработчик",
                    "total_applications": 50,
                    "unique_applications": 42,
                    "duplicates": 8
                }
            ]
        }

    def cleanup_old_hashes(self, days_old: int = 90) -> int:
        """
        Очистка старых хешей резюме

        Args:
            days_old: Возраст в днях

        Returns:
            int: Количество очищенных записей
        """
        # TODO: Реализовать очистку старых хешей
        # для освобождения места в БД

        return 0

    def validate_resume_data(self, resume_data: Dict[str, Any]) -> bool:
        """
        Валидация данных резюме перед хешированием

        Args:
            resume_data: Данные резюме

        Returns:
            bool: True если данные валидны для хеширования
        """
        required_fields = ["id", "title"]

        for field in required_fields:
            if not resume_data.get(field):
                logger.warning(f"Отсутствует обязательное поле '{field}' в резюме")
                return False

        return True