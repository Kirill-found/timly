"""
AI сервис для анализа резюме
Интеграция с OpenAI GPT-4o-mini для анализа кандидатов
"""
import json
import time
import hashlib
from typing import Dict, Any, List, Optional
import logging
import openai
import redis
from openai import AsyncOpenAI

from app.config import settings
from app.utils.exceptions import AIAnalysisError

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """
    AI анализатор резюме
    Использует GPT-4o-mini для анализа соответствия кандидата вакансии
    """

    def __init__(self):
        # Отключаем отладочное логирование OpenAI SDK (вызывает UnicodeEncodeError с кириллицей)
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)

        # Настройка HTTP прокси если указан
        import httpx
        http_client = None
        if hasattr(settings, 'OPENAI_PROXY_URL') and settings.OPENAI_PROXY_URL:
            logger.info(f"Используется прокси для OpenAI: {settings.OPENAI_PROXY_URL}")
            # httpx требует proxies в формате словаря для старых версий
            http_client = httpx.AsyncClient(
                proxies={
                    "http://": settings.OPENAI_PROXY_URL,
                    "https://": settings.OPENAI_PROXY_URL
                },
                timeout=60.0
            )

        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            http_client=http_client
        )
        self.model = settings.OPENAI_MODEL

        # Redis для кеширования результатов
        try:
            self.cache = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Проверка соединения
            self.cache.ping()
        except Exception as e:
            logger.warning(f"Redis недоступен, кеширование отключено: {e}")
            self.cache = None

    def _get_cache_key(self, vacancy_data: Dict, resume_data: Dict) -> str:
        """
        Генерация ключа кеша для анализа

        Args:
            vacancy_data: Данные вакансии
            resume_data: Данные резюме

        Returns:
            str: Ключ кеша
        """
        # Создание стабильного хеша из ключевых полей
        vacancy_hash = hashlib.md5(
            json.dumps(vacancy_data, sort_keys=True).encode()
        ).hexdigest()[:8]

        resume_hash = hashlib.md5(
            json.dumps(resume_data, sort_keys=True).encode()
        ).hexdigest()[:8]

        return f"analysis:{vacancy_hash}:{resume_hash}"

    def _get_cached_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Получение результата из кеша"""
        if not self.cache:
            return None

        try:
            cached = self.cache.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Ошибка чтения кеша: {e}")

        return None

    def _cache_analysis(self, cache_key: str, result: Dict[str, Any], ttl: int = 86400):
        """Сохранение результата в кеш (24 часа)"""
        if not self.cache:
            return

        try:
            self.cache.setex(
                cache_key,
                ttl,
                json.dumps(result, ensure_ascii=False)
            )
        except Exception as e:
            logger.warning(f"Ошибка записи в кеш: {e}")

    def _create_analysis_prompt(
        self,
        vacancy_data: Dict[str, Any],
        resume_data: Dict[str, Any]
    ) -> str:
        """
        Создание промпта для AI анализа

        Args:
            vacancy_data: Данные вакансии
            resume_data: Данные резюме (dict или JSON string)

        Returns:
            str: Промпт для GPT
        """
        # Парсинг resume_data если это JSON строка
        if isinstance(resume_data, str):
            try:
                resume_data = json.loads(resume_data)
            except json.JSONDecodeError:
                logger.error("Не удалось распарсить resume_data как JSON")
                resume_data = {}

        # Безопасное получение данных с проверкой на None
        if not resume_data or not isinstance(resume_data, dict):
            resume_data = {}

        # Извлекаем опыт работы для анализа
        experience_list = resume_data.get('experience', [])
        experience_text = ""
        if experience_list and isinstance(experience_list, list):
            for exp in experience_list[:3]:  # Берем последние 3 места работы
                if isinstance(exp, dict):
                    company = exp.get('company', {}).get('name', 'Не указано') if isinstance(exp.get('company'), dict) else 'Не указано'
                    position = exp.get('position', 'Не указано')
                    start = exp.get('start', {}).get('year', '') if isinstance(exp.get('start'), dict) else ''
                    end = exp.get('end', {}).get('year', 'н.в.') if exp.get('end') and isinstance(exp.get('end'), dict) else 'н.в.'
                    description = exp.get('description', '')[:200] if exp.get('description') else ''
                    experience_text += f"\n- {company}, {position} ({start}-{end}): {description}"

        return f"""## РОЛЬ И ЗАДАЧА
Ты — профессиональный AI-рекрутер с 15+ летним опытом в подборе персонала. Твоя задача — быстро и точно оценить соответствие кандидата требованиям вакансии.

## ПРИНЦИПЫ РАБОТЫ
1. **ОБЪЕКТИВНОСТЬ** — оценивай только факты из резюме, не додумывай
2. **ФОКУС НА РЕЗУЛЬТАТ** — конкретные выводы, а не рассуждения
3. **СТРУКТУРИРОВАННОСТЬ** — четкий JSON формат
4. **ПРАКТИЧНОСТЬ** — выводы должны быть сразу применимы

## ДАННЫЕ ДЛЯ АНАЛИЗА

### ВАКАНСИЯ:
Название: {vacancy_data.get('title', 'Не указано')}
Требуемые навыки: {', '.join(vacancy_data.get('key_skills', [])) or 'Не указаны'}
Требуемый опыт: {vacancy_data.get('experience', 'Не указан')}
Зарплатная вилка: {vacancy_data.get('salary_from', 0)} - {vacancy_data.get('salary_to', 0)} {vacancy_data.get('currency', 'RUB')}
Описание вакансии: {vacancy_data.get('description', '')[:500] if vacancy_data.get('description') else 'Не указано'}

### РЕЗЮМЕ КАНДИДАТА:
ФИО: {resume_data.get('first_name', '')} {resume_data.get('last_name', '')}
Текущая должность: {resume_data.get('title', 'Не указана')}
Возраст: {resume_data.get('age', 'Не указан')}
Город: {resume_data.get('area', {}).get('name', 'Не указан') if isinstance(resume_data.get('area'), dict) else 'Не указан'}
Общий опыт работы: {(resume_data.get('total_experience') or {}).get('months', 0) // 12} лет ({(resume_data.get('total_experience') or {}).get('months', 0) % 12} мес)
Ключевые навыки: {', '.join([skill.get('name', '') for skill in resume_data.get('skill_set', []) if isinstance(skill, dict)]) or 'Не указаны'}
Зарплатные ожидания: {(resume_data.get('salary') or {}).get('amount', 'Не указана')} {(resume_data.get('salary') or {}).get('currency', '')}
Опыт работы:{experience_text or ' Не указан'}

## КРИТЕРИИ ОЦЕНКИ

### Hard Skills (40% веса):
- Технические навыки из вакансии
- Инструменты и технологии
- Профессиональные сертификаты
- Релевантное образование

### Релевантный опыт (35% веса):
- Прямое соответствие должности
- Опыт в аналогичной индустрии
- Масштаб ответственности
- Измеримые достижения

### Soft Skills (15% веса):
- Коммуникативные навыки
- Лидерские качества
- Обучаемость и адаптивность

### Условия работы (10% веса):
- Зарплатные ожидания
- География
- Готовность к условиям

## КРАСНЫЕ ФЛАГИ (обязательно укажи если есть):
- Частая смена работы (>3 мест за 2 года)
- Пробелы в опыте (>6 месяцев без объяснения)
- Завышенные зарплатные ожидания (>40% от предложения)
- Несоответствие образования и опыта
- Отсутствие ключевых навыков из вакансии

## ЗЕЛЕНЫЕ ФЛАГИ (повышают оценку):
- Карьерный рост на предыдущих местах
- Конкретные достижения с цифрами
- Релевантные сертификаты
- Длительная работа в компаниях (>2 лет)

## ШКАЛА РЕКОМЕНДАЦИЙ:
- **hire** (90-100 баллов): Идеальный кандидат — приглашать немедленно
- **interview** (70-89 баллов): Сильный кандидат — пригласить на собеседование
- **maybe** (50-69 баллов): Средний кандидат — рассмотреть при нехватке лучших
- **reject** (0-49 баллов): Не подходит — отклонить

## ФОРМАТ ОТВЕТА (строгий JSON):

{{
    "score": <число 0-100>,
    "skills_match": <число 0-100>,
    "experience_match": <число 0-100>,
    "salary_match": "<match/higher/lower/unknown>",
    "strengths": ["сильная сторона 1", "сильная сторона 2", "сильная сторона 3"],
    "weaknesses": ["слабая сторона 1", "слабая сторона 2", "слабая сторона 3"],
    "red_flags": ["красный флаг 1"],
    "recommendation": "<hire/interview/maybe/reject>",
    "reasoning": "Краткое обоснование (2-3 предложения с конкретными фактами из резюме)"
}}

## ПРАВИЛА ДЛЯ СИЛЬНЫХ СТОРОН (strengths):
Определи **РОВНО 3** конкретных сильных стороны кандидата:
- Используй ТОЛЬКО факты из резюме, а не общие фразы
- Каждое предложение должно начинаться с действия или факта ("Управлял…", "Создал…", "Имеет опыт…")
- ЗАПРЕЩЕНО писать: "коммуникабельный", "стрессоустойчивый", "ответственный", "мотивированный"
- Привязывай выводы к вакансии, например:
  * "Подходит, так как уже работал с маркетплейсами Ozon/WB"
  * "Управлял командой из 15 человек — соответствует требованиям вакансии"
  * "Увеличил продажи на 40% за год — есть измеримые результаты"

## ПРАВИЛА ДЛЯ СЛАБЫХ СТОРОН (weaknesses):
Найди **РОВНО 3** слабые стороны:
- Тоже только факты, без воды
- Указывай, почему это может быть проблемой именно для ЭТОЙ вакансии
- Если в резюме не хватает информации — пиши "Не указано [что именно]"
- Примеры:
  * "Нет опыта работы с BI-инструментами — потребуется обучение Power BI"
  * "Не указаны результаты прошлых проектов — сложно оценить эффективность"
  * "Работал только в B2C — переход на B2B может потребовать адаптации"
  * "Частая смена работы (4 места за 2 года) — риск быстрого ухода"

## ВАЖНО:
- Указывай ТОЛЬКО факты из резюме
- НЕ придумывай данные
- Будь максимально конкретным в обосновании
- Фокусируйся на измеримых результатах
- Оценивай объективно, без стереотипов
- strengths и weaknesses должны содержать РОВНО по 3 элемента
"""

    async def analyze_resume(
        self,
        vacancy_data: Dict[str, Any],
        resume_data: Dict[str, Any],
        force_reanalysis: bool = False
    ) -> Dict[str, Any]:
        """
        Анализ резюме кандидата на соответствие вакансии

        Args:
            vacancy_data: Данные вакансии
            resume_data: Данные резюме
            force_reanalysis: Принудительный анализ (игнорировать кеш)

        Returns:
            Dict: Результат анализа

        Raises:
            AIAnalysisError: При ошибках анализа
        """
        start_time = time.time()

        try:
            # Проверка кеша
            cache_key = self._get_cache_key(vacancy_data, resume_data)

            if not force_reanalysis:
                cached_result = self._get_cached_analysis(cache_key)
                if cached_result:
                    logger.info(f"Результат анализа получен из кеша: {cache_key}")
                    return cached_result

            # Создание промпта
            prompt = self._create_analysis_prompt(vacancy_data, resume_data)

            # Вызов OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты эксперт HR аналитик. Отвечай только в формате JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Меньше творчества, больше точности
                max_tokens=1000,
                response_format={"type": "json_object"}
            )

            # Обработка ответа
            ai_response = response.choices[0].message.content

            try:
                analysis_result = json.loads(ai_response)
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга JSON ответа: {e}")
                logger.error(f"Ответ AI: {ai_response}")
                raise AIAnalysisError("Некорректный формат ответа от AI")

            # Добавление метаданных
            processing_time = int((time.time() - start_time) * 1000)
            analysis_result.update({
                "ai_model": self.model,
                "ai_tokens_used": response.usage.total_tokens,
                "ai_cost_rub": self._calculate_cost(response.usage.total_tokens),
                "processing_time_ms": processing_time
            })

            # Кеширование результата
            self._cache_analysis(cache_key, analysis_result)

            logger.info(
                f"AI анализ завершен за {processing_time}ms, "
                f"токенов: {response.usage.total_tokens}, "
                f"оценка: {analysis_result.get('score', 0)}"
            )

            return analysis_result

        except openai.RateLimitError:
            raise AIAnalysisError("Превышен лимит запросов к OpenAI API")

        except openai.APIError as e:
            logger.error(f"Ошибка OpenAI API: {e}")
            raise AIAnalysisError(f"Ошибка AI сервиса: {e}")

        except Exception as e:
            logger.error(f"Неожиданная ошибка при анализе: {e}")
            raise AIAnalysisError(f"Ошибка анализа резюме: {e}")

    async def analyze_batch(
        self,
        vacancy_data: Dict[str, Any],
        resumes_data: List[Dict[str, Any]],
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Пакетный анализ резюме

        Args:
            vacancy_data: Данные вакансии
            resumes_data: Список резюме для анализа
            max_concurrent: Максимум одновременных запросов

        Returns:
            List: Результаты анализов

        Raises:
            AIAnalysisError: При критических ошибках
        """
        if len(resumes_data) > 5:
            raise AIAnalysisError("Максимум 5 резюме за раз для оптимизации стоимости")

        import asyncio

        results = []
        semaphore = asyncio.Semaphore(max_concurrent)

        async def analyze_single(resume_data: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                try:
                    return await self.analyze_resume(vacancy_data, resume_data)
                except Exception as e:
                    logger.error(f"Ошибка анализа резюме {resume_data.get('id', 'unknown')}: {e}")
                    return {
                        "error": str(e),
                        "resume_id": resume_data.get("id"),
                        "status": "failed"
                    }

        # Выполнение анализов
        tasks = [analyze_single(resume) for resume in resumes_data]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Фильтрация успешных результатов
        successful_results = [
            result for result in results
            if isinstance(result, dict) and "error" not in result
        ]

        logger.info(
            f"Пакетный анализ: {len(successful_results)}/{len(resumes_data)} успешно"
        )

        return successful_results

    def _calculate_cost(self, total_tokens: int) -> float:
        """
        Расчет стоимости запроса в рублях

        Args:
            total_tokens: Общее количество токенов

        Returns:
            float: Стоимость в рублях (DECIMAL(6,2))
        """
        # GPT-4o-mini стоимость (примерно $0.15 за 1M токенов)
        cost_per_1k_tokens_usd = 0.00015  # $0.15 / 1000
        cost_usd = (total_tokens / 1000) * cost_per_1k_tokens_usd
        cost_rub = cost_usd * 90  # Примерный курс доллара
        return round(cost_rub, 2)  # В рублях с 2 знаками после запятой

    async def get_analysis_stats(self) -> Dict[str, Any]:
        """
        Статистика использования AI анализатора

        Returns:
            Dict: Статистика анализов
        """
        # TODO: Реализовать получение статистики из БД
        return {
            "total_analyses": 245,
            "analyses_today": 12,
            "total_cost_cents": 3450,
            "cost_today_cents": 180,
            "avg_score": 68.5,
            "cache_hit_rate": 0.35
        }