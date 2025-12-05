"""
Клиент для работы с HH.ru API
Обработка всех запросов к API hh.ru с retry логикой
Поддержка mock режима для разработки
"""
import httpx
import asyncio
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from app.config import settings
from app.utils.exceptions import HHIntegrationError
from app.services.hh_mock import HHMockService

logger = logging.getLogger(__name__)


class HHClient:
    """
    Клиент для интеграции с HH.ru API
    Использует токен работодателя для доступа к данным
    Поддерживает mock режим для разработки
    """

    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.hh.ru"
        self.timeout = 30.0
        self.is_mock_mode = settings.HH_MOCK_MODE

        # В mock режиме создаем mock сервис
        if self.is_mock_mode:
            self.mock_service = HHMockService()
            logger.info("HHClient работает в mock режиме")
            self.session = None
        else:
            # Создание HTTP клиента с настройками для реального API
            self.session = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "User-Agent": "Timly Resume Screening Platform (api@timly.ru)"
                },
                timeout=self.timeout,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
            self.mock_service = None
            logger.info("HHClient работает в реальном режиме с HH.ru API")

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def close(self):
        """Закрытие HTTP клиента"""
        if self.session:
            await self.session.aclose()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Выполнение HTTP запроса с retry логикой

        Args:
            method: HTTP метод
            endpoint: API endpoint
            params: GET параметры
            data: POST данные
            max_retries: Максимум попыток

        Returns:
            Dict: Ответ API

        Raises:
            HHIntegrationError: При ошибках API
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(max_retries + 1):
            try:
                response = await self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data
                )

                # Обработка rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limit hit, waiting {retry_after} seconds")

                    if attempt < max_retries:
                        await asyncio.sleep(retry_after)
                        continue

                    raise HHIntegrationError(
                        "Превышен лимит запросов к HH.ru API",
                        status_code=429
                    )

                # Проверка авторизации
                if response.status_code == 401:
                    raise HHIntegrationError(
                        "Недействительный или просроченный HH.ru токен",
                        status_code=401
                    )

                # Проверка доступа
                if response.status_code == 403:
                    raise HHIntegrationError(
                        "Токен HH.ru недействителен или истёк. Пожалуйста, обновите токен в настройках",
                        status_code=403
                    )

                # Успешный ответ
                if response.status_code == 200:
                    return response.json()

                # Другие ошибки
                if response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    error_message = error_data.get("description", f"HTTP {response.status_code}")

                    raise HHIntegrationError(
                        f"Ошибка HH.ru API: {error_message}",
                        status_code=response.status_code
                    )

            except httpx.TimeoutException:
                logger.warning(f"Timeout на попытке {attempt + 1}")
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise HHIntegrationError("Таймаут при обращении к HH.ru API")

            except httpx.RequestError as e:
                logger.error(f"Ошибка запроса на попытке {attempt + 1}: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise HHIntegrationError(f"Ошибка соединения с HH.ru API: {e}")

        raise HHIntegrationError("Превышено максимальное количество попыток")

    async def _make_request_full_url(
        self,
        url: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Выполнение HTTP GET запроса к полному URL (для collection URLs из API HH.ru)

        Args:
            url: Полный URL
            max_retries: Максимум попыток

        Returns:
            Dict: Ответ API

        Raises:
            HHIntegrationError: При ошибках API
        """
        for attempt in range(max_retries + 1):
            try:
                response = await self.session.get(url)

                # Обработка ошибок аналогично _make_request
                if response.status_code == 403:
                    raise HHIntegrationError(
                        "Токен HH.ru недействителен или истёк. Пожалуйста, обновите токен в настройках",
                        status_code=403
                    )

                if response.status_code == 401:
                    raise HHIntegrationError(
                        "Недействительный или просроченный HH.ru токен",
                        status_code=401
                    )

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    if attempt < max_retries:
                        await asyncio.sleep(retry_after)
                        continue
                    raise HHIntegrationError(
                        "Превышен лимит запросов к HH.ru API",
                        status_code=429
                    )

                if response.status_code == 200:
                    return response.json()

                if response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    error_message = error_data.get("description", f"HTTP {response.status_code}")
                    raise HHIntegrationError(
                        f"Ошибка HH.ru API: {error_message}",
                        status_code=response.status_code
                    )

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error на попытке {attempt + 1}: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise HHIntegrationError(f"HTTP ошибка: {e}")

            except httpx.TimeoutException:
                logger.warning(f"Timeout на попытке {attempt + 1}")
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise HHIntegrationError("Таймаут при обращении к HH.ru API")

            except httpx.RequestError as e:
                logger.error(f"Ошибка запроса на попытке {attempt + 1}: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise HHIntegrationError(f"Ошибка соединения с HH.ru API: {e}")

        raise HHIntegrationError("Превышено максимальное количество попыток")

    # Основные методы API
    async def test_connection(self) -> Dict[str, Any]:
        """
        Тестирование соединения и валидности токена

        Returns:
            Dict: Результат проверки токена
        """
        try:
            if self.is_mock_mode:
                # В mock режиме используем mock сервис
                return await self.mock_service.validate_mock_token(self.token)
            else:
                # Получение информации о работодателе через реальный API
                response = await self._make_request("GET", "/me")

                return {
                    "is_valid": True,
                    "employer_name": response.get("employer", {}).get("name"),
                    "employer_id": response.get("employer", {}).get("id"),
                    "error_message": None
                }

        except HHIntegrationError as e:
            logger.error(f"Ошибка валидации токена: {e}")
            return {
                "is_valid": False,
                "employer_name": None,
                "employer_id": None,
                "error_message": str(e)
            }

    async def get_employer_info(self) -> Dict[str, Any]:
        """
        Получение информации о работодателе
        Используется для валидации токена и получения названия компании

        Returns:
            Dict: Информация о работодателе
        """
        try:
            if self.is_mock_mode:
                # В mock режиме используем mock сервис
                return await self.mock_service.get_mock_employer_info()
            else:
                # Получение информации о работодателе через реальный API
                response = await self._make_request("GET", "/me")
                employer_data = response.get("employer", {})

                return {
                    "id": employer_data.get("id"),
                    "name": employer_data.get("name"),
                    "url": employer_data.get("alternate_url"),
                    "area": employer_data.get("area", {}).get("name"),
                    "type": employer_data.get("type", {}).get("name"),
                    "industries": employer_data.get("industries", [])
                }

        except Exception as e:
            logger.error(f"Ошибка получения информации о работодателе: {e}")
            raise HHIntegrationError(f"Не удалось получить информацию о компании: {e}")

    async def get_vacancies(self, page: int = 0, per_page: int = 20) -> Dict[str, Any]:
        """
        Получение списка вакансий работодателя

        Args:
            page: Номер страницы
            per_page: Количество вакансий на странице

        Returns:
            Dict: Список вакансий с пагинацией
        """
        try:
            if self.is_mock_mode:
                # В mock режиме используем mock сервис
                return await self.mock_service.get_mock_vacancies(page=page, per_page=per_page)
            else:
                # Реальный API HH.ru - получение вакансий работодателя
                # Используем endpoint /employer/vacancies
                params = {
                    "page": page,
                    "per_page": per_page
                }

                # Сначала получаем employer_id из /me используя _make_request для корректной обработки ошибок
                me_data = await self._make_request("GET", "/me")

                employer_id = me_data.get("employer", {}).get("id")
                if not employer_id:
                    raise HHIntegrationError("Токен не является токеном работодателя")

                # Используем публичный endpoint /vacancies с фильтром по employer_id
                params["employer_id"] = employer_id

                data = await self._make_request("GET", "/vacancies", params=params)

                logger.info(f"✅ Получено {len(data.get('items', []))} вакансий с HH.ru API")
                return data

        except Exception as e:
            logger.error(f"Ошибка получения вакансий: {e}")
            raise HHIntegrationError(f"Не удалось получить вакансии: {e}")

    async def get_vacancy_details(self, vacancy_id: str) -> Dict[str, Any]:
        """
        Получение детальной информации о вакансии

        Args:
            vacancy_id: ID вакансии в HH.ru

        Returns:
            Dict: Детали вакансии
        """
        try:
            if self.is_mock_mode:
                # В mock режиме используем mock сервис
                return await self.mock_service.get_mock_vacancy_details(vacancy_id)
            else:
                # Получение через реальный API
                return await self._make_request("GET", f"/vacancies/{vacancy_id}")

        except Exception as e:
            logger.error(f"Ошибка получения деталей вакансии {vacancy_id}: {e}")
            raise HHIntegrationError(f"Не удалось получить вакансию: {e}")

    async def get_applications(self, vacancy_id: str, page: int = 0, per_page: int = 100) -> Dict[str, Any]:
        """
        Получение откликов на вакансию

        Args:
            vacancy_id: ID вакансии
            page: Номер страницы
            per_page: Количество откликов на странице

        Returns:
            Dict: Отклики с пагинацией
        """
        try:
            if self.is_mock_mode:
                # В mock режиме используем mock сервис
                return await self.mock_service.get_mock_applications(
                    vacancy_id=vacancy_id,
                    page=page,
                    per_page=per_page
                )
            else:
                # Реальный API HH.ru - получение откликов через коллекции
                # Сначала получаем список коллекций
                collections_data = await self._make_request(
                    "GET",
                    "/negotiations",
                    params={"vacancy_id": vacancy_id}
                )

                # Собираем все отклики из всех коллекций
                all_items = []

                for collection in collections_data.get("collections", []):
                    # Используем sub_collections (они содержат реальные URL)
                    sub_collections = collection.get("sub_collections", [])

                    for sub_collection in sub_collections:
                        # Используем только root коллекции (они содержат все отклики)
                        if not sub_collection.get("root_collection", False):
                            continue

                        total = sub_collection.get("counters", {}).get("total", 0)
                        if total == 0:
                            continue

                        collection_url = sub_collection.get("url")
                        collection_id = sub_collection.get("id")

                        logger.debug(f"Загрузка коллекции {collection_id} для вакансии {vacancy_id} ({total} откликов)")

                        # Загружаем все страницы коллекции
                        collection_page = 0
                        collection_items = []

                        while True:
                            # Добавляем параметр page к URL коллекции (per_page не поддерживается для коллекций)
                            page_url = f"{collection_url}&page={collection_page}"

                            # Используем _make_request_full_url для корректной обработки ошибок
                            coll_data = await self._make_request_full_url(page_url)

                            items = coll_data.get("items", [])
                            if not items:  # Если больше нет откликов, выходим
                                break

                            # Добавляем collection_id к каждому элементу для фильтрации
                            for item in items:
                                item["_collection_id"] = collection_id

                            collection_items.extend(items)

                            # Проверяем, есть ли ещё страницы
                            current_page = coll_data.get("page", collection_page)
                            total_pages = coll_data.get("pages", 1)

                            logger.debug(f"Загружена страница {current_page + 1}/{total_pages} коллекции {collection_id}: {len(items)} откликов")

                            if current_page >= total_pages - 1:  # Последняя страница
                                break

                            collection_page += 1

                        all_items.extend(collection_items)
                        logger.debug(f"Получено {len(collection_items)} откликов из коллекции {collection_id}")

                logger.info(f"Получено {len(all_items)} откликов на вакансию {vacancy_id}")

                # Возвращаем в том же формате что и mock
                return {
                    "items": all_items,
                    "found": len(all_items),
                    "pages": 1,
                    "page": page,
                    "per_page": per_page
                }

        except Exception as e:
            logger.error(f"Ошибка получения откликов для вакансии {vacancy_id}: {e}")
            raise HHIntegrationError(f"Не удалось получить отклики: {e}")

    async def get_resume_details(self, resume_id: str) -> Dict[str, Any]:
        """
        Получение детальной информации о резюме

        Args:
            resume_id: ID резюме в HH.ru

        Returns:
            Dict: Детали резюме
        """
        try:
            if self.is_mock_mode:
                # В mock режиме используем mock сервис
                return await self.mock_service.get_mock_resume_details(resume_id)
            else:
                # Получение через реальный API
                return await self._make_request("GET", f"/resumes/{resume_id}")

        except Exception as e:
            logger.error(f"Ошибка получения резюме {resume_id}: {e}")
            raise HHIntegrationError(f"Не удалось получить резюме: {e}")

    # Утилиты
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

    async def get_api_stats(self) -> Dict[str, Any]:
        """
        Получение статистики использования API

        Returns:
            Dict: Статистика лимитов и использования
        """
        if self.is_mock_mode:
            # В mock режиме используем mock сервис
            return await self.mock_service.get_mock_api_stats()
        else:
            # TODO: Реализовать получение статистики через реальный API
            # Пока используем mock данные
            mock_service = HHMockService()
            return await mock_service.get_mock_api_stats()

    # Алиасы для синхронизации (используются в sync_jobs.py)
    async def get_my_vacancies(self, page: int = 0, per_page: int = 100) -> Dict[str, Any]:
        """
        Алиас для get_vacancies - получение вакансий работодателя

        Args:
            page: Номер страницы
            per_page: Количество на странице

        Returns:
            Dict: Список вакансий
        """
        return await self.get_vacancies(page=page, per_page=per_page)

    async def get_vacancy_applications(self, vacancy_id: str, page: int = 0, per_page: int = 100) -> Dict[str, Any]:
        """
        Алиас для get_applications - получение откликов на вакансию

        Args:
            vacancy_id: ID вакансии
            page: Номер страницы
            per_page: Количество на странице

        Returns:
            Dict: Список откликов
        """
        return await self.get_applications(vacancy_id=vacancy_id, page=page, per_page=per_page)

    # ==================== ПОИСК ПО БАЗЕ РЕЗЮМЕ ====================

    async def search_resumes(
        self,
        text: str,
        area: Optional[str] = None,
        experience: Optional[str] = None,
        salary_from: Optional[int] = None,
        salary_to: Optional[int] = None,
        age_from: Optional[int] = None,
        age_to: Optional[int] = None,
        gender: Optional[str] = None,
        education_level: Optional[str] = None,
        job_search_status: Optional[str] = None,
        relocation: Optional[str] = None,
        order_by: str = "relevance",
        page: int = 0,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """
        Поиск резюме в базе HH.ru

        Args:
            text: Поисковый запрос (ключевые слова, должность, навыки)
            area: ID региона (1 - Москва, 2 - Санкт-Петербург и т.д.)
            experience: Опыт работы (noExperience, between1And3, between3And6, moreThan6)
            salary_from: Минимальная зарплата
            salary_to: Максимальная зарплата
            age_from: Минимальный возраст
            age_to: Максимальный возраст
            gender: Пол (male, female)
            education_level: Уровень образования (secondary, special_secondary, unfinished_higher, higher, bachelor, master, candidate, doctor)
            job_search_status: Статус поиска работы (active, passive, not_looking)
            relocation: Готовность к переезду (living_or_relocation, living, relocation)
            order_by: Сортировка (relevance, publication_time, salary_desc, salary_asc)
            page: Номер страницы
            per_page: Количество на странице (макс 100)

        Returns:
            Dict: Результаты поиска с пагинацией
        """
        try:
            if self.is_mock_mode:
                return await self.mock_service.search_mock_resumes(
                    text=text,
                    page=page,
                    per_page=per_page
                )

            # Формируем параметры поиска
            params = {
                "text": text,
                "page": page,
                "per_page": min(per_page, 100),  # API ограничение
                "order_by": order_by
            }

            # Добавляем опциональные фильтры
            if area:
                params["area"] = area
            if experience:
                params["experience"] = experience
            if salary_from:
                params["salary_from"] = salary_from
            if salary_to:
                params["salary_to"] = salary_to
            if age_from:
                params["age_from"] = age_from
            if age_to:
                params["age_to"] = age_to
            if gender:
                params["gender"] = gender
            if education_level:
                params["education_level"] = education_level
            if job_search_status:
                params["job_search_status"] = job_search_status
            if relocation:
                params["relocation"] = relocation

            logger.info(f"Поиск резюме: text='{text}', area={area}, experience={experience}")

            data = await self._make_request("GET", "/resumes", params=params)

            logger.info(f"✅ Найдено {data.get('found', 0)} резюме по запросу '{text}'")
            return data

        except Exception as e:
            logger.error(f"Ошибка поиска резюме: {e}")
            raise HHIntegrationError(f"Не удалось выполнить поиск резюме: {e}")

    async def get_resume_search_dictionaries(self) -> Dict[str, Any]:
        """
        Получение справочников для поиска резюме
        (регионы, опыт, образование и т.д.)

        Returns:
            Dict: Справочники для фильтров поиска
        """
        try:
            if self.is_mock_mode:
                return await self.mock_service.get_mock_dictionaries()

            # Получаем справочники из API
            dictionaries = await self._make_request("GET", "/dictionaries")

            # Также получаем регионы
            areas = await self._make_request("GET", "/areas")

            return {
                "experience": dictionaries.get("experience", []),
                "education_level": dictionaries.get("education_level", []),
                "gender": dictionaries.get("gender", []),
                "job_search_status": dictionaries.get("resume_search_job_search_status", []),
                "relocation": dictionaries.get("relocation_type", []),
                "order_by": [
                    {"id": "relevance", "name": "По релевантности"},
                    {"id": "publication_time", "name": "По дате обновления"},
                    {"id": "salary_desc", "name": "По убыванию зарплаты"},
                    {"id": "salary_asc", "name": "По возрастанию зарплаты"}
                ],
                "areas": areas
            }

        except Exception as e:
            logger.error(f"Ошибка получения справочников: {e}")
            raise HHIntegrationError(f"Не удалось получить справочники: {e}")

    async def get_resume_views_history(self, resume_id: str) -> Dict[str, Any]:
        """
        Получение истории просмотров резюме работодателем

        Args:
            resume_id: ID резюме

        Returns:
            Dict: История просмотров
        """
        try:
            if self.is_mock_mode:
                return {"items": [], "found": 0}

            return await self._make_request("GET", f"/resumes/{resume_id}/views")

        except Exception as e:
            logger.error(f"Ошибка получения истории просмотров резюме {resume_id}: {e}")
            raise HHIntegrationError(f"Не удалось получить историю просмотров: {e}")