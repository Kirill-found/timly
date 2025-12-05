"""
Сервис поиска по базе резюме
Интеграция с HH.ru API и AI анализом
"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.vacancy import Vacancy
from app.models.resume_search import ResumeSearch, SearchCandidate, SearchStatus
from app.services.hh_client import HHClient
from app.services.ai_analyzer import AIAnalyzer
from app.services.encryption import token_encryption
from app.utils.exceptions import HHIntegrationError, AIAnalysisError

logger = logging.getLogger(__name__)


class ResumeSearchService:
    """
    Сервис для поиска и анализа резюме из базы HH.ru
    """

    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self._hh_client: Optional[HHClient] = None
        self._ai_analyzer: Optional[AIAnalyzer] = None

    async def _get_hh_client(self) -> HHClient:
        """Получение HH клиента с токеном пользователя"""
        if self._hh_client is None:
            if not self.user.has_hh_token:
                raise HHIntegrationError("HH.ru токен не настроен. Добавьте токен в настройках.")

            decrypted_token = token_encryption.decrypt(self.user.encrypted_hh_token)
            self._hh_client = HHClient(decrypted_token)

        return self._hh_client

    def _get_ai_analyzer(self) -> AIAnalyzer:
        """Получение AI анализатора"""
        if self._ai_analyzer is None:
            self._ai_analyzer = AIAnalyzer()
        return self._ai_analyzer

    async def run_search(self, search: ResumeSearch, max_results: int = 100) -> Dict[str, Any]:
        """
        Запуск поиска по базе резюме HH.ru

        Args:
            search: Поисковый проект
            max_results: Максимальное количество резюме для загрузки

        Returns:
            Dict: Результат поиска
        """
        try:
            # Обновляем статус
            search.status = SearchStatus.RUNNING
            search.last_run_at = datetime.utcnow()
            search.error_message = None
            self.db.commit()

            # Получаем HH клиент
            hh_client = await self._get_hh_client()

            # Формируем параметры поиска из фильтров
            filters = search.filters or {}

            # Выполняем поиск
            logger.info(f"Запуск поиска '{search.name}': query='{search.search_query}'")

            all_resumes = []
            page = 0
            per_page = min(50, max_results)  # API ограничение

            while len(all_resumes) < max_results:
                result = await hh_client.search_resumes(
                    text=search.search_query,
                    area=filters.get("area"),
                    experience=filters.get("experience"),
                    salary_from=filters.get("salary_from"),
                    salary_to=filters.get("salary_to"),
                    age_from=filters.get("age_from"),
                    age_to=filters.get("age_to"),
                    gender=filters.get("gender"),
                    education_level=filters.get("education_level"),
                    job_search_status=filters.get("job_search_status"),
                    relocation=filters.get("relocation"),
                    page=page,
                    per_page=per_page
                )

                items = result.get("items", [])
                if not items:
                    break

                all_resumes.extend(items)
                search.total_found = result.get("found", 0)

                # Проверяем, есть ли ещё страницы
                total_pages = result.get("pages", 1)
                if page >= total_pages - 1:
                    break

                page += 1

            # Ограничиваем количество результатов
            all_resumes = all_resumes[:max_results]

            # Сохраняем кандидатов в БД
            new_count = 0
            updated_count = 0

            for resume_item in all_resumes:
                hh_resume_id = resume_item.get("id")
                if not hh_resume_id:
                    continue

                # Проверяем, есть ли уже этот кандидат
                existing = self.db.query(SearchCandidate).filter(
                    SearchCandidate.search_id == search.id,
                    SearchCandidate.hh_resume_id == hh_resume_id
                ).first()

                if existing:
                    # Обновляем данные
                    self._update_candidate_from_resume(existing, resume_item)
                    updated_count += 1
                else:
                    # Создаём нового кандидата
                    candidate = self._create_candidate_from_resume(search.id, resume_item)
                    self.db.add(candidate)
                    new_count += 1

            # Обновляем статистику поиска
            search.processed_count = len(all_resumes)
            search.status = SearchStatus.COMPLETED
            self.db.commit()

            logger.info(f"Поиск '{search.name}' завершён: найдено {search.total_found}, загружено {len(all_resumes)} (новых: {new_count}, обновлено: {updated_count})")

            return {
                "status": "completed",
                "total_found": search.total_found,
                "processed_count": search.processed_count,
                "new_candidates": new_count,
                "updated_candidates": updated_count
            }

        except Exception as e:
            logger.error(f"Ошибка поиска '{search.name}': {e}")
            search.status = SearchStatus.FAILED
            search.error_message = str(e)
            self.db.commit()
            raise

    def _create_candidate_from_resume(self, search_id: str, resume_data: Dict) -> SearchCandidate:
        """Создание кандидата из данных резюме"""
        # Извлекаем данные из резюме
        salary_data = resume_data.get("salary", {}) or {}
        area_data = resume_data.get("area", {}) or {}
        experience_data = resume_data.get("total_experience", {}) or {}

        # Получаем навыки
        skills = []
        for skill in resume_data.get("skill_set", []):
            if isinstance(skill, str):
                skills.append(skill)
            elif isinstance(skill, dict):
                skills.append(skill.get("name", ""))

        candidate = SearchCandidate(
            search_id=search_id,
            hh_resume_id=resume_data.get("id"),
            first_name=resume_data.get("first_name"),
            last_name=resume_data.get("last_name"),
            middle_name=resume_data.get("middle_name"),
            title=resume_data.get("title"),
            age=resume_data.get("age"),
            gender=resume_data.get("gender", {}).get("id") if isinstance(resume_data.get("gender"), dict) else None,
            area=area_data.get("name") if isinstance(area_data, dict) else None,
            salary=salary_data.get("amount") if isinstance(salary_data, dict) else None,
            currency=salary_data.get("currency", "RUB") if isinstance(salary_data, dict) else "RUB",
            experience_years=experience_data.get("months") if isinstance(experience_data, dict) else None,
            skills=skills,
            resume_data=resume_data
        )

        return candidate

    def _update_candidate_from_resume(self, candidate: SearchCandidate, resume_data: Dict):
        """Обновление данных кандидата"""
        salary_data = resume_data.get("salary", {}) or {}
        area_data = resume_data.get("area", {}) or {}

        candidate.first_name = resume_data.get("first_name")
        candidate.last_name = resume_data.get("last_name")
        candidate.title = resume_data.get("title")
        candidate.age = resume_data.get("age")
        candidate.area = area_data.get("name") if isinstance(area_data, dict) else None
        candidate.salary = salary_data.get("amount") if isinstance(salary_data, dict) else None
        candidate.resume_data = resume_data

    async def analyze_candidates(
        self,
        search: ResumeSearch,
        candidate_ids: Optional[List[str]] = None,
        force_reanalysis: bool = False
    ) -> Dict[str, Any]:
        """
        AI анализ кандидатов

        Args:
            search: Поисковый проект
            candidate_ids: ID конкретных кандидатов (все, если не указано)
            force_reanalysis: Переанализировать уже проанализированных

        Returns:
            Dict: Результат анализа
        """
        try:
            # Обновляем статус
            search.status = SearchStatus.ANALYZING
            self.db.commit()

            # Получаем кандидатов для анализа
            query = self.db.query(SearchCandidate).filter(SearchCandidate.search_id == search.id)

            if candidate_ids:
                query = query.filter(SearchCandidate.id.in_(candidate_ids))

            if not force_reanalysis:
                query = query.filter(SearchCandidate.is_analyzed == False)

            candidates = query.all()

            if not candidates:
                search.status = SearchStatus.DONE
                self.db.commit()
                return {
                    "status": "completed",
                    "analyzed_count": 0,
                    "message": "Нет кандидатов для анализа"
                }

            # Получаем данные вакансии для контекста (если есть)
            vacancy_data = None
            if search.vacancy_id:
                vacancy = self.db.query(Vacancy).filter(Vacancy.id == search.vacancy_id).first()
                if vacancy:
                    vacancy_data = {
                        "title": vacancy.title,
                        "description": vacancy.description,
                        "key_skills": vacancy.key_skills,
                        "experience": vacancy.experience,
                        "salary_from": vacancy.salary_from,
                        "salary_to": vacancy.salary_to
                    }

            # Если вакансия не указана, используем поисковый запрос как контекст
            if not vacancy_data:
                vacancy_data = {
                    "title": search.search_query,
                    "description": f"Поиск кандидатов по запросу: {search.search_query}",
                    "key_skills": search.search_query.split(),
                    "filters": search.filters
                }

            # Анализируем кандидатов
            ai_analyzer = self._get_ai_analyzer()
            analyzed_count = 0
            errors_count = 0

            for candidate in candidates:
                try:
                    # Анализируем резюме
                    analysis_result = await ai_analyzer.analyze_resume(
                        vacancy_data=vacancy_data,
                        resume_data=candidate.resume_data
                    )

                    # Сохраняем результаты
                    candidate.is_analyzed = True
                    candidate.ai_score = analysis_result.get("score", 0)
                    candidate.ai_recommendation = analysis_result.get("recommendation", "consider")
                    candidate.ai_summary = analysis_result.get("summary", "")
                    candidate.ai_strengths = analysis_result.get("strengths", [])
                    candidate.ai_weaknesses = analysis_result.get("weaknesses", [])
                    candidate.ai_analysis_data = analysis_result
                    candidate.analyzed_at = datetime.utcnow()

                    analyzed_count += 1
                    search.analyzed_count = analyzed_count

                    self.db.commit()

                except Exception as e:
                    logger.error(f"Ошибка анализа кандидата {candidate.id}: {e}")
                    errors_count += 1

            # Обновляем статус поиска
            search.status = SearchStatus.DONE
            self.db.commit()

            logger.info(f"Анализ '{search.name}' завершён: проанализировано {analyzed_count}, ошибок {errors_count}")

            return {
                "status": "completed",
                "analyzed_count": analyzed_count,
                "errors_count": errors_count
            }

        except Exception as e:
            logger.error(f"Ошибка анализа кандидатов '{search.name}': {e}")
            search.status = SearchStatus.FAILED
            search.error_message = str(e)
            self.db.commit()
            raise

    async def get_dictionaries(self) -> Dict[str, Any]:
        """Получение справочников для фильтров поиска"""
        try:
            hh_client = await self._get_hh_client()
            return await hh_client.get_resume_search_dictionaries()
        except Exception as e:
            logger.error(f"Ошибка получения справочников: {e}")
            # Возвращаем базовые справочники
            return self._get_default_dictionaries()

    def _get_default_dictionaries(self) -> Dict[str, Any]:
        """Справочники по умолчанию"""
        return {
            "experience": [
                {"id": "noExperience", "name": "Нет опыта"},
                {"id": "between1And3", "name": "От 1 года до 3 лет"},
                {"id": "between3And6", "name": "От 3 до 6 лет"},
                {"id": "moreThan6", "name": "Более 6 лет"}
            ],
            "education_level": [
                {"id": "secondary", "name": "Среднее"},
                {"id": "special_secondary", "name": "Среднее специальное"},
                {"id": "unfinished_higher", "name": "Неоконченное высшее"},
                {"id": "higher", "name": "Высшее"},
                {"id": "bachelor", "name": "Бакалавр"},
                {"id": "master", "name": "Магистр"},
                {"id": "candidate", "name": "Кандидат наук"},
                {"id": "doctor", "name": "Доктор наук"}
            ],
            "gender": [
                {"id": "male", "name": "Мужской"},
                {"id": "female", "name": "Женский"}
            ],
            "job_search_status": [
                {"id": "active", "name": "Активно ищет работу"},
                {"id": "passive", "name": "Рассматривает предложения"},
                {"id": "not_looking", "name": "Не ищет работу"}
            ],
            "relocation": [
                {"id": "living_or_relocation", "name": "Живёт или готов к переезду"},
                {"id": "living", "name": "Только живёт в указанном регионе"},
                {"id": "relocation", "name": "Только готов к переезду"}
            ],
            "order_by": [
                {"id": "relevance", "name": "По релевантности"},
                {"id": "publication_time", "name": "По дате обновления"},
                {"id": "salary_desc", "name": "По убыванию зарплаты"},
                {"id": "salary_asc", "name": "По возрастанию зарплаты"}
            ],
            "areas": [
                {"id": "1", "name": "Москва", "parent_id": None},
                {"id": "2", "name": "Санкт-Петербург", "parent_id": None},
                {"id": "3", "name": "Екатеринбург", "parent_id": None},
                {"id": "4", "name": "Новосибирск", "parent_id": None},
                {"id": "88", "name": "Казань", "parent_id": None},
                {"id": "66", "name": "Нижний Новгород", "parent_id": None},
                {"id": "76", "name": "Ростов-на-Дону", "parent_id": None},
                {"id": "104", "name": "Краснодар", "parent_id": None}
            ]
        }

    async def close(self):
        """Закрытие соединений"""
        if self._hh_client:
            await self._hh_client.close()
