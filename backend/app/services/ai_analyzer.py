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
        Создание промпта для AI анализа (v2 - композитный скоринг)

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
                    experience_text += f"\n  - {company}, {position} ({start}-{end}): {description}"

        # Извлекаем навыки как список строк
        skills_list = []
        for skill in resume_data.get('skill_set', []):
            if isinstance(skill, dict):
                skills_list.append(skill.get('name', ''))
            elif isinstance(skill, str):
                skills_list.append(skill)
        skills_text = ', '.join(skills_list) if skills_list else 'Не указаны'

        return f"""## РОЛЬ
Ты — AI-ассистент рекрутера. Твоя задача — предварительный скрининг резюме.
Ты НЕ принимаешь решение о найме, ты помогаешь рекрутеру быстрее находить релевантных кандидатов.

## ПРИНЦИПЫ
1. **НЕ ДИСКРИМИНИРУЙ** — игнорируй возраст, пол, национальность
2. **УЧИТЫВАЙ КОНТЕКСТ** — частая смена работы в IT/стартапах ≠ красный флаг
3. **ПРИЗНАВАЙ НЕОПРЕДЕЛЁННОСТЬ** — если данных мало, ставь confidence: "low"
4. **БУДЬ КОНКРЕТЕН** — не "хороший опыт", а "5 лет в e-commerce, рост от junior до lead"
5. **БУДЬ СТРОГИМ** — оценка 5 должна быть РЕДКОЙ (идеальный кандидат), большинство — 3-4
6. **ВЕРИФИЦИРУЙ ДАННЫЕ** — нереалистичный опыт (>15 лет в молодой индустрии) = red flag

## ДАННЫЕ ДЛЯ АНАЛИЗА

### ВАКАНСИЯ:
Название: {vacancy_data.get('title', 'Не указано')}
Требуемые навыки: {', '.join(vacancy_data.get('key_skills', [])) or 'Не указаны'}
Требуемый опыт: {vacancy_data.get('experience', 'Не указан')}
Зарплатная вилка: {vacancy_data.get('salary_from', 0)} - {vacancy_data.get('salary_to', 0)} {vacancy_data.get('currency', 'RUB')}
Описание: {vacancy_data.get('description', '')[:500] if vacancy_data.get('description') else 'Не указано'}

### РЕЗЮМЕ КАНДИДАТА:
ФИО: {resume_data.get('first_name', '')} {resume_data.get('last_name', '')}
Текущая должность: {resume_data.get('title', 'Не указана')}
Город: {resume_data.get('area', {}).get('name', 'Не указан') if isinstance(resume_data.get('area'), dict) else 'Не указан'}
Общий опыт: {(resume_data.get('total_experience') or {}).get('months', 0) // 12} лет {(resume_data.get('total_experience') or {}).get('months', 0) % 12} мес
Ключевые навыки: {skills_text}
Зарплатные ожидания: {(resume_data.get('salary') or {}).get('amount', 'Не указана')} {(resume_data.get('salary') or {}).get('currency', '')}
Опыт работы:{experience_text or ' Не указан'}

## ВАЛИДАЦИЯ ДАННЫХ (КРИТИЧЕСКИ ВАЖНО!)

### Проверка реалистичности опыта:
- Wildberries основан в 2004, активно с 2015 — опыт >10 лет в WB НЕРЕАЛИСТИЧЕН
- Ozon как маркетплейс с 2018 — опыт >7 лет в Ozon НЕРЕАЛИСТИЧЕН
- TikTok с 2016, в РФ активно с 2019 — опыт >5 лет НЕРЕАЛИСТИЧЕН
- Если заявлен нереалистичный опыт → снижай stability до 2, добавляй в red_flags

### Проверка зарплатных ожиданий:
- НИЖЕ вилки на >30% — это WARNING, не плюс! (возможно: overqualified не готов работать, занижает опыт, демпинг)
- В пределах вилки ±20% — нормально
- ВЫШЕ вилки на >40% — red flag

## ЗАДАЧА: ОЦЕНКА ПО 4 КРИТЕРИЯМ (шкала 1-5)

### ВАЖНО О КАЛИБРОВКЕ:
- Оценка **5** = ИСКЛЮЧИТЕЛЬНЫЙ кандидат (топ-10%), дается РЕДКО
- Оценка **4** = ХОРОШИЙ кандидат, соответствует требованиям
- Оценка **3** = СРЕДНИЙ кандидат, есть gaps но можно рассмотреть
- Оценка **2** = СЛАБЫЙ кандидат, значительные недостатки
- Оценка **1** = НЕ ПОДХОДИТ

### 1. РЕЛЕВАНТНОСТЬ ПОЗИЦИИ (relevance) — вес 35%
Насколько последняя позиция и опыт соответствуют вакансии?
- 5: Точное совпадение должности + индустрии + уровня (РЕДКО!)
- 4: Похожая позиция или смежная индустрия
- 3: Частичное совпадение, потребуется адаптация
- 2: Слабое соответствие, большой gap
- 1: Не релевантно

### 2. ЭКСПЕРТИЗА В НАВЫКАХ (expertise) — вес 30%
Какой % требуемых навыков есть у кандидата + глубина?
- 5: 90%+ навыков + ПОДТВЕРЖДЕННАЯ глубокая экспертиза (достижения с цифрами)
- 4: 70-89% навыков, уверенное владение
- 3: 50-69% навыков, базовый уровень
- 2: 30-49% навыков, потребуется обучение
- 1: <30% навыков

### 3. КАРЬЕРНАЯ ТРАЕКТОРИЯ (trajectory) — вес 20%
Как развивалась карьера кандидата?
- 5: Стабильный рост С ДОКАЗАТЕЛЬСТВАМИ (повышения, расширение команды, рост метрик)
- 4: Позитивная динамика с небольшими паузами
- 3: Стабильная карьера без явного роста
- 2: Частые смены без видимой логики ИЛИ недостаток данных
- 1: Негативная динамика или большие пробелы >1 года

### 4. СТАБИЛЬНОСТЬ И РИСКИ (stability) — вес 15%
Оценка рисков при найме:
- 5: Стабильная ВЕРИФИЦИРУЕМАЯ история, нет red flags
- 4: Минимальные риски, объяснимые переходы
- 3: Умеренные риски, требует уточнения на интервью
- 2: Заметные риски (нереалистичный опыт, несоответствие ЗП, частые смены)
- 1: Серьёзные red flags

## КРАСНЫЕ ФЛАГИ (обязательно учитывай!):
- **Нереалистичный опыт** (>10 лет в WB/Ozon, >15 лет в e-commerce России)
- Частая смена работы БЕЗ логики (не просто >3 за 2 года, а без карьерного смысла)
- Пробелы >6 мес без объяснения
- Завышенные ЗП ожидания (>40% от вилки)
- **Заниженные ЗП ожидания** (>30% ниже вилки — подозрительно!)
- Несоответствие заявленных навыков и опыта
- Общие фразы без конкретики (нет цифр, нет достижений)

## ЖЁЛТЫЕ ФЛАГИ (предупреждения, влияют на confidence):
- ЗП ожидания ниже рынка — возможно overqualified или скрытые проблемы
- Много компаний без известных имен — сложно верифицировать
- Нет измеримых достижений — только должности

## ЗЕЛЁНЫЕ ФЛАГИ (бонусы, могут поднять оценку на 1 балл):
- Карьерный рост на предыдущих местах С ЦИФРАМИ
- Измеримые достижения ("увеличил продажи на 40%", "команда 10 человек")
- Релевантные сертификаты
- Опыт в ИЗВЕСТНЫХ компаниях индустрии (WB, Ozon, Яндекс.Маркет — но проверяй сроки!)

## ФОРМАТ ОТВЕТА (строгий JSON):

{{
    "scores": {{
        "relevance": <1-5>,
        "expertise": <1-5>,
        "trajectory": <1-5>,
        "stability": <1-5>
    }},

    "confidence": "<high/medium/low>",

    "skills_analysis": {{
        "matching": ["навык1", "навык2"],
        "missing": ["навык3"],
        "match_percent": <0-100>
    }},

    "experience_years": <число>,
    "last_position": "<должность>",
    "last_company": "<компания>",
    "candidate_salary": <число или 0>,
    "salary_match": "<match/higher/lower/unknown>",

    "pros": ["конкретный плюс 1", "плюс 2"],
    "cons": ["конкретный минус 1"],
    "red_flags": [],
    "green_flags": [],

    "interview_questions": [
        "Вопрос для уточнения gap 1",
        "Вопрос про опыт 2"
    ],

    "reasoning": "2-3 предложения с ФАКТАМИ и цифрами",
    "summary": "10-15 слов: роль, опыт, ключевое преимущество/риск"
}}

## ПРАВИЛА:

### Для pros/cons:
- От 1 до 5 пунктов (не фиксированно 3!)
- ТОЛЬКО факты из резюме
- ЗАПРЕЩЕНО: "коммуникабельный", "ответственный", "мотивированный"
- ПРАВИЛЬНО: "Руководил командой 10 человек", "Вырос от junior до lead за 2 года"

### Для interview_questions:
- 2-3 вопроса для уточнения gaps или рисков
- Конкретные, не общие ("Расскажите про опыт с Redis" вместо "Расскажите о себе")

### Для reasoning:
ПЛОХО: "Кандидат имеет релевантный опыт"
ХОРОШО: "5 лет в e-commerce, последние 2 года — team lead. Нет опыта с K8s — потребуется онбординг"

### Для summary:
ПЛОХО: "Подходящий кандидат для позиции"
ХОРОШО: "Senior Python, 6 лет, ex-Яндекс, растущий тренд, gap в DevOps"

### Для confidence:
- "high": достаточно данных для уверенной оценки
- "medium": есть пробелы, но общая картина ясна
- "low": мало данных, оценка приблизительная

## ВАЖНО:
- Оценивай ТОЛЬКО по фактам из резюме
- НЕ придумывай данные
- Если информации нет — укажи это в cons и снизь confidence
"""

    def _calculate_composite_score(self, scores: Dict[str, int]) -> Dict[str, Any]:
        """
        Расчёт композитного скора из оценок 1-5 (v2 - строгая калибровка)

        Args:
            scores: Словарь с оценками {relevance, expertise, trajectory, stability}

        Returns:
            Dict: rank_score, tier, recommendation
        """
        # Веса критериев
        weights = {
            "relevance": 0.35,
            "expertise": 0.30,
            "trajectory": 0.20,
            "stability": 0.15
        }

        # Расчёт взвешенного среднего
        weighted_sum = 0
        for key, weight in weights.items():
            score = scores.get(key, 3)  # По умолчанию 3
            weighted_sum += score * weight

        # Масштабируем 1-5 → 0-100
        rank_score = int((weighted_sum - 1) * 25)  # 1→0, 5→100

        # СТРОГАЯ калибровка tier:
        # - Tier A: только если средняя >= 4.3 (большинство оценок 4-5, без троек)
        # - Tier B: 3.3 - 4.29 (хороший средний кандидат)
        # - Tier C: < 3.3 (ниже среднего)
        if weighted_sum >= 4.3:
            tier = "A"
        elif weighted_sum >= 3.3:
            tier = "B"
        else:
            tier = "C"

        # СТРОГИЕ рекомендации:
        # - hire: только tier A с rank_score >= 85 (исключительные кандидаты)
        # - interview: хорошие кандидаты, стоит рассмотреть
        # - maybe: есть сомнения, но можно попробовать
        # - reject: не соответствует требованиям
        if rank_score >= 85 and tier == "A":
            recommendation = "hire"
        elif rank_score >= 70:
            recommendation = "interview"
        elif rank_score >= 50:
            recommendation = "maybe"
        else:
            recommendation = "reject"

        return {
            "rank_score": rank_score,
            "tier": tier,
            "recommendation": recommendation,
            "weighted_average": round(weighted_sum, 2)
        }

    def _enrich_analysis_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обогащение результата анализа композитным скором и обратной совместимостью

        Args:
            result: Исходный результат от AI

        Returns:
            Dict: Обогащённый результат
        """
        # Извлекаем scores из нового формата
        scores = result.get("scores", {})

        # Если нет нового формата, пробуем старый
        if not scores:
            # Обратная совместимость со старым форматом
            old_score = result.get("score", 50)
            return result

        # Расчёт композитного скора
        composite = self._calculate_composite_score(scores)

        # Добавляем вычисленные поля
        result["rank_score"] = composite["rank_score"]
        result["tier"] = composite["tier"]
        result["recommendation"] = composite["recommendation"]

        # Обратная совместимость: добавляем старые поля
        result["score"] = composite["rank_score"]
        result["skills_match"] = result.get("skills_analysis", {}).get("match_percent", 50)
        result["experience_match"] = int(scores.get("relevance", 3) * 20)

        # Маппинг новых полей на старые для совместимости
        if "skills_analysis" in result:
            result["matching_skills"] = result["skills_analysis"].get("matching", [])
            result["skill_gaps"] = result["skills_analysis"].get("missing", [])

        # strengths/weaknesses из pros/cons
        result["strengths"] = result.get("pros", [])
        result["weaknesses"] = result.get("cons", [])

        # summary_one_line из summary
        result["summary_one_line"] = result.get("summary", "")

        # career_trajectory из trajectory score
        trajectory_score = scores.get("trajectory", 3)
        if trajectory_score >= 4:
            result["career_trajectory"] = "growth"
        elif trajectory_score == 3:
            result["career_trajectory"] = "stable"
        elif trajectory_score == 2:
            result["career_trajectory"] = "decline"
        else:
            result["career_trajectory"] = "start"

        return result

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
            Dict: Результат анализа с композитным скором

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
                        "content": "Ты AI-ассистент рекрутера. Отвечай ТОЛЬКО в JSON. Оценивай по шкале 1-5. Используй факты."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1500,
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

            # Обогащаем результат композитным скором
            analysis_result = self._enrich_analysis_result(analysis_result)

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
                f"tier: {analysis_result.get('tier', '?')}, "
                f"rank_score: {analysis_result.get('rank_score', 0)}"
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