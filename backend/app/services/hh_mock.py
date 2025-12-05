"""
Mock сервис для HH.ru API
Используется для разработки и тестирования до подключения реального API
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from tests.fixtures import (
    MOCK_VACANCIES,
    MOCK_APPLICATIONS,
    get_mock_vacancy_by_id,
    get_mock_vacancies_page,
    get_mock_applications_by_vacancy_id,
    get_mock_application_by_id,
    get_mock_resume_by_id
)

logger = logging.getLogger(__name__)


class HHMockService:
    """
    Mock сервис для имитации HH.ru API
    Возвращает реалистичные данные для разработки и тестирования
    """

    def __init__(self, user_id: str = None):
        self.user_id = user_id
        self._simulate_delays = True  # Имитация задержек сети

    async def _simulate_network_delay(self, delay_ms: int = 200):
        """Имитация задержки сети для более реалистичного тестирования"""
        if self._simulate_delays:
            await asyncio.sleep(delay_ms / 1000.0)

    async def get_mock_employer_info(self) -> Dict[str, Any]:
        """
        Имитация получения информации о работодателе

        Returns:
            Dict: Информация о работодателе
        """
        await self._simulate_network_delay(150)

        return {
            "id": "mock_employer_123",
            "name": "ТестКомпания IT Solutions",
            "url": "https://api.hh.ru/employers/mock_employer_123",
            "alternate_url": "https://hh.ru/employer/mock_employer_123",
            "area": {
                "id": "1",
                "name": "Москва",
                "url": "https://api.hh.ru/areas/1"
            },
            "type": {
                "id": "company",
                "name": "Компания"
            },
            "industries": [
                {
                    "id": "7.540",
                    "name": "Разработка программного обеспечения"
                }
            ],
            "description": "Компания занимается разработкой корпоративных IT решений",
            "site_url": "https://testcompany.ru",
            "trusted": True,
            "logo_urls": {
                "original": "https://img.hhcdn.ru/employer-logo/mock123.png",
                "240": "https://img.hhcdn.ru/employer-logo/mock123_240.png",
                "90": "https://img.hhcdn.ru/employer-logo/mock123_90.png"
            }
        }

    async def get_mock_vacancies(self, page: int = 0, per_page: int = 20) -> Dict[str, Any]:
        """
        Получение mock вакансий с пагинацией

        Args:
            page: Номер страницы (начиная с 0)
            per_page: Количество вакансий на странице

        Returns:
            Dict: Список вакансий с пагинацией
        """
        await self._simulate_network_delay(300)

        logger.info(f"Получение mock вакансий: страница {page}, по {per_page} на странице")

        result = get_mock_vacancies_page(page=page, per_page=per_page)

        # Добавляем дополнительные поля для совместимости с HH.ru API
        for vacancy in result["items"]:
            vacancy["employer_id"] = vacancy["employer"]["id"]
            vacancy["manager"] = {"id": f"manager_{vacancy['id']}"}

        return result

    async def get_mock_vacancy_details(self, vacancy_id: str) -> Dict[str, Any]:
        """
        Получение детальной информации о вакансии

        Args:
            vacancy_id: ID вакансии

        Returns:
            Dict: Детали вакансии
        """
        await self._simulate_network_delay(250)

        logger.info(f"Получение деталей mock вакансии: {vacancy_id}")

        vacancy = get_mock_vacancy_by_id(vacancy_id)
        if not vacancy:
            raise Exception(f"Вакансия {vacancy_id} не найдена")

        return vacancy

    async def get_mock_applications(
        self,
        vacancy_id: str,
        page: int = 0,
        per_page: int = 100
    ) -> Dict[str, Any]:
        """
        Получение mock откликов на вакансию

        Args:
            vacancy_id: ID вакансии
            page: Номер страницы
            per_page: Количество откликов на странице

        Returns:
            Dict: Список откликов с пагинацией
        """
        await self._simulate_network_delay(400)

        logger.info(f"Получение mock откликов для вакансии {vacancy_id}: страница {page}")

        result = get_mock_applications_by_vacancy_id(
            vacancy_id=vacancy_id,
            page=page,
            per_page=per_page
        )

        # Добавляем дополнительную информацию
        for application in result["items"]:
            # Убеждаемся что у каждого отклика есть все необходимые поля
            application.setdefault("state", {"id": "response", "name": "Отклик"})
            application.setdefault("has_updates", False)
            application.setdefault("viewed_by_opponent", True)
            application.setdefault("source", "response")

            # Добавляем ID вакансии в контекст
            application["vacancy_id"] = vacancy_id

            # Обогащаем данные резюме
            resume = application.get("resume", {})
            if resume:
                resume.setdefault("id", f"resume_{application['id']}")
                resume.setdefault("url", f"https://api.hh.ru/resumes/{resume['id']}")
                resume.setdefault("alternate_url", f"https://hh.ru/resume/{resume['id']}")

        return result

    async def get_mock_resume_details(self, resume_id: str) -> Dict[str, Any]:
        """
        Получение детальной информации о резюме

        Args:
            resume_id: ID резюме

        Returns:
            Dict: Детали резюме
        """
        await self._simulate_network_delay(350)

        logger.info(f"Получение деталей mock резюме: {resume_id}")

        resume = get_mock_resume_by_id(resume_id)
        if not resume:
            raise Exception(f"Резюме {resume_id} не найдено")

        return resume

    async def get_mock_application_details(self, application_id: str) -> Dict[str, Any]:
        """
        Получение детальной информации об отклике

        Args:
            application_id: ID отклика

        Returns:
            Dict: Детали отклика
        """
        await self._simulate_network_delay(200)

        logger.info(f"Получение деталей mock отклика: {application_id}")

        application = get_mock_application_by_id(application_id)
        if not application:
            raise Exception(f"Отклик {application_id} не найден")

        return application

    async def validate_mock_token(self, token: str) -> Dict[str, Any]:
        """
        Валидация mock токена

        Args:
            token: HH.ru API токен

        Returns:
            Dict: Результат валидации
        """
        await self._simulate_network_delay(100)

        # Mock валидация - принимаем любой токен длиннее 10 символов
        is_valid = len(token) >= 10

        if is_valid:
            employer_info = await self.get_mock_employer_info()
            return {
                "is_valid": True,
                "employer_name": employer_info["name"],
                "employer_id": employer_info["id"],
                "error_message": None
            }
        else:
            return {
                "is_valid": False,
                "employer_name": None,
                "employer_id": None,
                "error_message": "Токен слишком короткий для mock режима"
            }

    async def get_mock_api_stats(self) -> Dict[str, Any]:
        """
        Получение mock статистики API

        Returns:
            Dict: Статистика лимитов
        """
        await self._simulate_network_delay(50)

        return {
            "requests_made_today": 156,
            "requests_limit_per_day": 5000,
            "requests_remaining": 4844,
            "reset_time": (datetime.now() + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            ).isoformat() + "+03:00"
        }

    def get_resume_hash(self, resume_data: Dict[str, Any]) -> str:
        """
        Создание хеша резюме для дедупликации

        Args:
            resume_data: Данные резюме

        Returns:
            str: MD5 хеш ключевых полей
        """
        import hashlib

        # Ключевые поля для определения уникальности
        key_fields = [
            resume_data.get("id", ""),
            resume_data.get("title", ""),
            resume_data.get("first_name", ""),
            resume_data.get("last_name", ""),
            str(resume_data.get("age", "")),
        ]

        # Создание стабильного хеша
        hash_string = "|".join(key_fields).lower().strip()
        return hashlib.md5(hash_string.encode()).hexdigest()

    def disable_network_delays(self):
        """Отключение имитации задержек сети (для быстрого тестирования)"""
        self._simulate_delays = False
        logger.info("Mock network delays disabled")

    def enable_network_delays(self):
        """Включение имитации задержек сети"""
        self._simulate_delays = True
        logger.info("Mock network delays enabled")


# Глобальный экземпляр для использования в других модулях
mock_hh_service = HHMockService()


# Функции для обратной совместимости
async def get_mock_vacancies(page: int = 0, per_page: int = 20) -> Dict[str, Any]:
    """Получить mock вакансии (функция обертка)"""
    return await mock_hh_service.get_mock_vacancies(page=page, per_page=per_page)


async def get_mock_applications(
    vacancy_id: str,
    page: int = 0,
    per_page: int = 100
) -> Dict[str, Any]:
    """Получить mock отклики (функция обертка)"""
    return await mock_hh_service.get_mock_applications(
        vacancy_id=vacancy_id,
        page=page,
        per_page=per_page
    )


# ==================== MOCK ПОИСК РЕЗЮМЕ ====================

# Генерация mock резюме для поиска
MOCK_SEARCH_RESUMES = [
    {
        "id": "search_resume_001",
        "title": "Python Developer",
        "first_name": "Алексей",
        "last_name": "Петров",
        "middle_name": "Иванович",
        "age": 28,
        "gender": {"id": "male", "name": "Мужской"},
        "area": {"id": "1", "name": "Москва"},
        "salary": {"amount": 180000, "currency": "RUB"},
        "total_experience": {"months": 48},
        "skill_set": ["Python", "Django", "FastAPI", "PostgreSQL", "Docker", "Redis"],
        "experience": [
            {
                "company": "TechCorp",
                "position": "Senior Python Developer",
                "start": "2021-01",
                "end": None,
                "description": "Разработка высоконагруженных сервисов"
            }
        ],
        "education": {
            "level": {"id": "higher", "name": "Высшее"},
            "primary": [{"name": "МГУ", "year": 2018}]
        }
    },
    {
        "id": "search_resume_002",
        "title": "Senior Python Developer",
        "first_name": "Мария",
        "last_name": "Сидорова",
        "middle_name": "Александровна",
        "age": 32,
        "gender": {"id": "female", "name": "Женский"},
        "area": {"id": "1", "name": "Москва"},
        "salary": {"amount": 250000, "currency": "RUB"},
        "total_experience": {"months": 96},
        "skill_set": ["Python", "Django", "FastAPI", "AWS", "Kubernetes", "Machine Learning"],
        "experience": [
            {
                "company": "AI Solutions",
                "position": "Team Lead Python",
                "start": "2020-03",
                "end": None,
                "description": "Руководство командой из 5 разработчиков, разработка ML pipeline"
            }
        ],
        "education": {
            "level": {"id": "master", "name": "Магистр"},
            "primary": [{"name": "МФТИ", "year": 2015}]
        }
    },
    {
        "id": "search_resume_003",
        "title": "Backend Developer",
        "first_name": "Дмитрий",
        "last_name": "Козлов",
        "middle_name": None,
        "age": 25,
        "gender": {"id": "male", "name": "Мужской"},
        "area": {"id": "2", "name": "Санкт-Петербург"},
        "salary": {"amount": 120000, "currency": "RUB"},
        "total_experience": {"months": 24},
        "skill_set": ["Python", "Flask", "PostgreSQL", "Git", "Linux"],
        "experience": [
            {
                "company": "StartupHub",
                "position": "Python Developer",
                "start": "2022-06",
                "end": None,
                "description": "Разработка REST API для мобильного приложения"
            }
        ],
        "education": {
            "level": {"id": "higher", "name": "Высшее"},
            "primary": [{"name": "СПбГУ", "year": 2022}]
        }
    },
    {
        "id": "search_resume_004",
        "title": "Full-stack разработчик",
        "first_name": "Елена",
        "last_name": "Новикова",
        "middle_name": "Сергеевна",
        "age": 29,
        "gender": {"id": "female", "name": "Женский"},
        "area": {"id": "1", "name": "Москва"},
        "salary": {"amount": 200000, "currency": "RUB"},
        "total_experience": {"months": 60},
        "skill_set": ["Python", "Django", "React", "TypeScript", "PostgreSQL", "Docker"],
        "experience": [
            {
                "company": "WebDev Pro",
                "position": "Full-stack Developer",
                "start": "2019-08",
                "end": None,
                "description": "Разработка веб-приложений полного цикла"
            }
        ],
        "education": {
            "level": {"id": "higher", "name": "Высшее"},
            "primary": [{"name": "ВШЭ", "year": 2017}]
        }
    },
    {
        "id": "search_resume_005",
        "title": "Data Engineer",
        "first_name": "Артём",
        "last_name": "Волков",
        "middle_name": "Дмитриевич",
        "age": 31,
        "gender": {"id": "male", "name": "Мужской"},
        "area": {"id": "1", "name": "Москва"},
        "salary": {"amount": 280000, "currency": "RUB"},
        "total_experience": {"months": 84},
        "skill_set": ["Python", "Apache Spark", "Airflow", "Kafka", "Clickhouse", "SQL"],
        "experience": [
            {
                "company": "DataCorp",
                "position": "Senior Data Engineer",
                "start": "2018-01",
                "end": None,
                "description": "Построение ETL пайплайнов, работа с Big Data"
            }
        ],
        "education": {
            "level": {"id": "master", "name": "Магистр"},
            "primary": [{"name": "Бауманка", "year": 2016}]
        }
    },
    {
        "id": "search_resume_006",
        "title": "Junior Python Developer",
        "first_name": "Иван",
        "last_name": "Смирнов",
        "middle_name": "Петрович",
        "age": 23,
        "gender": {"id": "male", "name": "Мужской"},
        "area": {"id": "2", "name": "Санкт-Петербург"},
        "salary": {"amount": 80000, "currency": "RUB"},
        "total_experience": {"months": 12},
        "skill_set": ["Python", "Django", "Git", "HTML", "CSS"],
        "experience": [
            {
                "company": "WebStudio",
                "position": "Junior Developer",
                "start": "2023-01",
                "end": None,
                "description": "Разработка и поддержка веб-сайтов"
            }
        ],
        "education": {
            "level": {"id": "higher", "name": "Высшее"},
            "primary": [{"name": "ИТМО", "year": 2023}]
        }
    },
    {
        "id": "search_resume_007",
        "title": "DevOps Engineer",
        "first_name": "Ольга",
        "last_name": "Михайлова",
        "middle_name": "Владимировна",
        "age": 27,
        "gender": {"id": "female", "name": "Женский"},
        "area": {"id": "1", "name": "Москва"},
        "salary": {"amount": 220000, "currency": "RUB"},
        "total_experience": {"months": 48},
        "skill_set": ["Python", "Kubernetes", "Docker", "Terraform", "AWS", "CI/CD"],
        "experience": [
            {
                "company": "CloudTech",
                "position": "DevOps Engineer",
                "start": "2020-06",
                "end": None,
                "description": "Настройка и поддержка инфраструктуры в облаке"
            }
        ],
        "education": {
            "level": {"id": "higher", "name": "Высшее"},
            "primary": [{"name": "МИФИ", "year": 2019}]
        }
    },
    {
        "id": "search_resume_008",
        "title": "ML Engineer",
        "first_name": "Николай",
        "last_name": "Федоров",
        "middle_name": "Алексеевич",
        "age": 30,
        "gender": {"id": "male", "name": "Мужской"},
        "area": {"id": "1", "name": "Москва"},
        "salary": {"amount": 300000, "currency": "RUB"},
        "total_experience": {"months": 72},
        "skill_set": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "MLOps", "NLP"],
        "experience": [
            {
                "company": "AI Lab",
                "position": "Senior ML Engineer",
                "start": "2019-01",
                "end": None,
                "description": "Разработка и внедрение ML моделей в продакшн"
            }
        ],
        "education": {
            "level": {"id": "candidate", "name": "Кандидат наук"},
            "primary": [{"name": "МГУ, ВМК", "year": 2018}]
        }
    }
]


class HHMockService(HHMockService):
    """Расширение mock сервиса для поиска резюме"""

    async def search_mock_resumes(
        self,
        text: str,
        page: int = 0,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """
        Mock поиск по базе резюме

        Args:
            text: Поисковый запрос
            page: Номер страницы
            per_page: Количество на странице

        Returns:
            Dict: Результаты поиска
        """
        await self._simulate_network_delay(400)

        logger.info(f"Mock поиск резюме: text='{text}', page={page}")

        # Фильтруем резюме по запросу (простой поиск по навыкам и должности)
        search_terms = text.lower().split()
        filtered_resumes = []

        for resume in MOCK_SEARCH_RESUMES:
            # Проверяем совпадение в навыках или должности
            skills_lower = [s.lower() for s in resume.get("skill_set", [])]
            title_lower = resume.get("title", "").lower()

            for term in search_terms:
                if any(term in skill for skill in skills_lower) or term in title_lower:
                    filtered_resumes.append(resume)
                    break

        # Если ничего не найдено по фильтрам - возвращаем все
        if not filtered_resumes:
            filtered_resumes = MOCK_SEARCH_RESUMES.copy()

        # Пагинация
        total = len(filtered_resumes)
        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_items = filtered_resumes[start_idx:end_idx]

        return {
            "items": page_items,
            "found": total,
            "pages": (total + per_page - 1) // per_page,
            "page": page,
            "per_page": per_page
        }

    async def get_mock_dictionaries(self) -> Dict[str, Any]:
        """
        Mock справочники для поиска

        Returns:
            Dict: Справочники
        """
        await self._simulate_network_delay(100)

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
                {"id": "higher", "name": "Высшее"},
                {"id": "bachelor", "name": "Бакалавр"},
                {"id": "master", "name": "Магистр"},
                {"id": "candidate", "name": "Кандидат наук"}
            ],
            "gender": [
                {"id": "male", "name": "Мужской"},
                {"id": "female", "name": "Женский"}
            ],
            "job_search_status": [
                {"id": "active", "name": "Активно ищет работу"},
                {"id": "passive", "name": "Рассматривает предложения"}
            ],
            "relocation": [
                {"id": "living_or_relocation", "name": "Живёт или готов к переезду"},
                {"id": "living", "name": "Только живёт в указанном регионе"}
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
                {"id": "4", "name": "Новосибирск", "parent_id": None}
            ]
        }