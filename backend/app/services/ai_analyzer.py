"""
AI сервис для анализа резюме v3.0
Интеграция с OpenAI GPT-4o для анализа кандидатов

v3.0 Changes:
- Tier-1 компании (бонусные баллы)
- Skill Provenance (навык указан vs использовался)
- Gross/Net зарплата
- Контекстный анализ пробелов (декрет, саббатикал)
- Junior mode (пет-проекты)
- Светофор вердикт
- Английский язык как hard filter
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

# Tier-1 компании для бонусных баллов
TIER1_COMPANIES = [
    # Tech Giants
    "яндекс", "yandex", "сбер", "sber", "тинькофф", "tinkoff", "t-bank",
    "вк", "vk", "mail.ru", "мейл", "avito", "авито", "ozon", "озон",
    "wildberries", "вайлдберриз", "wb", "lamoda", "ламода",
    # International
    "google", "гугл", "meta", "facebook", "amazon", "microsoft", "apple",
    "netflix", "uber", "spotify", "airbnb", "stripe", "shopify",
    # Russian Tech
    "касперский", "kaspersky", "positive technologies", "позитив",
    "jetbrains", "джетбрейнс", "miro", "миро", "notion",
    # Fintech
    "revolut", "wise", "n26", "альфа-банк", "alfa-bank", "райффайзен",
    # E-commerce
    "aliexpress", "алиэкспресс", "cdek", "сдэк", "boxberry",
    # Consulting
    "mckinsey", "bcg", "bain", "deloitte", "pwc", "kpmg", "ey",
]


class AIAnalyzer:
    """
    AI анализатор резюме v3.0
    Использует GPT-4o для глубокого анализа соответствия кандидата вакансии
    """

    def __init__(self):
        # Отключаем отладочное логирование OpenAI SDK
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)

        # Настройка HTTP прокси если указан
        import httpx
        http_client = None
        if hasattr(settings, 'OPENAI_PROXY_URL') and settings.OPENAI_PROXY_URL:
            logger.info(f"Используется прокси для OpenAI: {settings.OPENAI_PROXY_URL}")
            http_client = httpx.AsyncClient(
                proxies={
                    "http://": settings.OPENAI_PROXY_URL,
                    "https://": settings.OPENAI_PROXY_URL
                },
                timeout=90.0
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
            self.cache.ping()
        except Exception as e:
            logger.warning(f"Redis недоступен, кеширование отключено: {e}")
            self.cache = None

    def _get_cache_key(self, vacancy_data: Dict, resume_data: Dict) -> str:
        """Генерация ключа кеша для анализа"""
        vacancy_hash = hashlib.md5(
            json.dumps(vacancy_data, sort_keys=True).encode()
        ).hexdigest()[:8]
        resume_hash = hashlib.md5(
            json.dumps(resume_data, sort_keys=True).encode()
        ).hexdigest()[:8]
        return f"analysis:v3:{vacancy_hash}:{resume_hash}"

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
            self.cache.setex(cache_key, ttl, json.dumps(result, ensure_ascii=False))
        except Exception as e:
            logger.warning(f"Ошибка записи в кеш: {e}")

    def _detect_tier1_companies(self, experience_text: str) -> List[str]:
        """Определение Tier-1 компаний в опыте кандидата"""
        found = []
        text_lower = experience_text.lower()
        for company in TIER1_COMPANIES:
            if company in text_lower:
                found.append(company)
        return list(set(found))

    def _create_analysis_prompt(
        self,
        vacancy_data: Dict[str, Any],
        resume_data: Dict[str, Any]
    ) -> str:
        """
        Создание промпта для AI анализа v3.0

        Включает:
        - Tier-1 компании
        - Skill Provenance
        - Gross/Net зарплата
        - Контекстный анализ пробелов
        - Junior mode
        - Светофор
        """
        # Парсинг resume_data если это JSON строка
        if isinstance(resume_data, str):
            try:
                resume_data = json.loads(resume_data)
            except json.JSONDecodeError:
                logger.error("Не удалось распарсить resume_data как JSON")
                resume_data = {}

        if not resume_data or not isinstance(resume_data, dict):
            resume_data = {}

        # === ПОЛНОЕ извлечение опыта работы (без обрезки!) ===
        experience_list = resume_data.get('experience', [])
        experience_text = ""
        companies_list = []

        if experience_list and isinstance(experience_list, list):
            for idx, exp in enumerate(experience_list[:5]):  # До 5 мест работы
                if isinstance(exp, dict):
                    company = exp.get('company', {}).get('name', 'Не указано') if isinstance(exp.get('company'), dict) else 'Не указано'
                    companies_list.append(company)
                    position = exp.get('position', 'Не указано')

                    # Даты
                    start_year = exp.get('start', {}).get('year', '') if isinstance(exp.get('start'), dict) else ''
                    start_month = exp.get('start', {}).get('month', '') if isinstance(exp.get('start'), dict) else ''
                    end_year = exp.get('end', {}).get('year', 'н.в.') if exp.get('end') and isinstance(exp.get('end'), dict) else 'н.в.'
                    end_month = exp.get('end', {}).get('month', '') if exp.get('end') and isinstance(exp.get('end'), dict) else ''

                    period = f"{start_month or ''}/{start_year}" if start_month else str(start_year)
                    period += f" - {end_month or ''}/{end_year}" if end_month else f" - {end_year}"

                    # ПОЛНОЕ описание задач (критически важно для Skill Provenance!)
                    description = exp.get('description', '') or ''

                    experience_text += f"""
### Место работы #{idx + 1}
**Компания:** {company}
**Должность:** {position}
**Период:** {period}
**Задачи и достижения:**
{description if description else 'Не указаны'}
"""

        # Определяем Tier-1 компании
        tier1_found = self._detect_tier1_companies(experience_text + ' '.join(companies_list))

        # === Навыки ===
        skills_list = []
        for skill in resume_data.get('skill_set', []):
            if isinstance(skill, dict):
                skills_list.append(skill.get('name', ''))
            elif isinstance(skill, str):
                skills_list.append(skill)
        skills_text = ', '.join(skills_list) if skills_list else 'Не указаны'

        # === Раздел "Обо мне" (ПОЛНЫЙ, без обрезки) ===
        about_text = resume_data.get('skills', '') or resume_data.get('about', '') or ''

        # === Сопроводительное письмо ===
        cover_letter = resume_data.get('cover_letter', '') or resume_data.get('message', '') or ''

        # === Образование ===
        education_list = resume_data.get('education', [])
        education_text = ""
        if education_list and isinstance(education_list, list):
            for edu in education_list[:3]:
                if isinstance(edu, dict):
                    name = edu.get('name', '')
                    result = edu.get('result', '')
                    year = edu.get('year', '')
                    education_text += f"\n- {name} ({year}): {result}" if result else f"\n- {name} ({year})"

        # === Языки ===
        languages = resume_data.get('language', [])
        languages_text = ""
        if languages and isinstance(languages, list):
            for lang in languages:
                if isinstance(lang, dict):
                    name = lang.get('name', '')
                    level = lang.get('level', {}).get('name', '') if isinstance(lang.get('level'), dict) else ''
                    languages_text += f"\n- {name}: {level}"

        # === Зарплата кандидата ===
        candidate_salary = (resume_data.get('salary') or {}).get('amount', 0)
        candidate_currency = (resume_data.get('salary') or {}).get('currency', 'RUR')

        # === Общий опыт ===
        total_months = (resume_data.get('total_experience') or {}).get('months', 0)
        total_years = total_months // 12
        total_months_remainder = total_months % 12

        # === Определение типа вакансии ===
        vacancy_title = vacancy_data.get('title', '').lower()
        is_junior = any(word in vacancy_title for word in ['junior', 'джуниор', 'стажер', 'trainee', 'intern'])
        is_it_role = any(word in vacancy_title for word in [
            'developer', 'разработчик', 'программист', 'engineer', 'devops', 'qa', 'тестировщик',
            'frontend', 'backend', 'fullstack', 'data', 'analyst', 'аналитик', 'product', 'продакт',
            'дизайнер', 'designer', 'marketing', 'маркетолог'
        ])

        # === ПОЛНОЕ описание вакансии (БЕЗ ОБРЕЗКИ!) ===
        vacancy_description = vacancy_data.get('description', '') or 'Не указано'
        vacancy_skills = ', '.join(vacancy_data.get('key_skills', [])) or 'Не указаны'

        # === Зарплатная вилка вакансии ===
        salary_from = vacancy_data.get('salary_from', 0) or 0
        salary_to = vacancy_data.get('salary_to', 0) or 0
        salary_currency = vacancy_data.get('currency', 'RUB')

        return f"""## РОЛЬ
Ты — опытный IT-рекрутер с 10+ летним стажем. Ты проводишь первичный скрининг резюме.
Твоя задача — НЕ отсеять хорошего кандидата (false negative хуже false positive).
Ты даёшь рекрутеру **факты и конкретику**, чтобы он принял решение.

## КРИТИЧЕСКИ ВАЖНЫЕ ПРИНЦИПЫ

### 1. SKILL PROVENANCE (Проверка навыков)
Навык в списке "Skills" ≠ реальный навык!
- Ищи ДОКАЗАТЕЛЬСТВА навыка в описании задач на местах работы
- Если навык указан в Skills, но НЕ упомянут ни в одном описании работы → "unverified_skills"
- Если навык указан И подтверждён задачами → "verified_skills"

### 2. TIER-1 КОМПАНИИ (Качество школы)
Опыт в топовых компаниях = бонус к оценке:
**Tier-1 IT:** Яндекс, Сбер, Тинькофф, VK, Авито, Ozon, Wildberries, Google, Meta, Amazon
**Tier-1 Консалтинг:** McKinsey, BCG, Bain, Deloitte, PwC, KPMG
{"**В резюме найдены Tier-1:** " + ", ".join(tier1_found) if tier1_found else "**Tier-1 компании не найдены**"}

### 3. ЗАРПЛАТА: GROSS vs NET
- Кандидаты обычно указывают NET (на руки)
- Вакансии часто указывают GROSS (до налогов)
- NET × 1.15 ≈ GROSS (учитывай 13-15% налог)
- Если разница в пределах 20% после конвертации — это ОК

### 4. ПРОБЕЛЫ В КАРЬЕРЕ (Context Matters)
НЕ наказывай за:
- Декретный отпуск (1-3 года — норма)
- Саббатикал/burnout recovery (до 1 года)
- Переезд в другую страну
- Учёба/MBA/курсы
Помечай как risk ТОЛЬКО необъяснённые пробелы >12 месяцев

### 5. JUNIOR MODE {"(АКТИВЕН)" if is_junior else "(НЕ АКТИВЕН)"}
{"Для джуниор-позиций: пет-проекты, GitHub, курсы = реальный опыт с коэффициентом 0.5" if is_junior else ""}

### 6. ЧАСТАЯ СМЕНА РАБОТЫ
{"IT/Стартапы: смена каждые 1.5-2 года — НОРМА, не red flag" if is_it_role else "Традиционные отрасли: ожидается стаж 3+ года на месте"}

---

## ДАННЫЕ ДЛЯ АНАЛИЗА

### ВАКАНСИЯ
**Название:** {vacancy_data.get('title', 'Не указано')}
**Требуемые навыки:** {vacancy_skills}
**Требуемый опыт:** {vacancy_data.get('experience', 'Не указан')}
**Зарплатная вилка:** {salary_from} - {salary_to} {salary_currency} {"(предположительно GROSS)" if salary_from > 100000 else ""}
**Полное описание вакансии:**
\"\"\"
{vacancy_description}
\"\"\"

### КАНДИДАТ
**ФИО:** {resume_data.get('first_name', '')} {resume_data.get('last_name', '')}
**Текущая/последняя должность:** {resume_data.get('title', 'Не указана')}
**Город:** {resume_data.get('area', {}).get('name', 'Не указан') if isinstance(resume_data.get('area'), dict) else 'Не указан'}
**Общий опыт:** {total_years} лет {total_months_remainder} мес
**Зарплатные ожидания:** {candidate_salary} {candidate_currency} {"(предположительно NET)" if candidate_salary else "не указаны"}
**Навыки в профиле:** {skills_text}
**Языки:** {languages_text or 'Не указаны'}
**Образование:** {education_text or 'Не указано'}

**Обо мне:**
\"\"\"
{about_text or 'Не указано'}
\"\"\"

**Сопроводительное письмо:**
\"\"\"
{cover_letter or 'Не указано'}
\"\"\"

### ОПЫТ РАБОТЫ (ДЕТАЛЬНО)
{experience_text or 'Опыт работы не указан'}

---

## ЗАДАНИЕ

### ШАГ 1: АНАЛИЗ НАВЫКОВ (Chain of Thought)
1. Выпиши требуемые навыки из вакансии
2. Для каждого навыка проверь:
   - Есть в списке Skills кандидата?
   - Есть доказательство в описании работы? (цитата или задача)
3. Раздели на: verified (подтверждённые), unverified (только в списке), missing (отсутствуют)

### ШАГ 2: ОЦЕНКА ПО РУБРИКЕ (1-5)

**RELEVANCE (Релевантность позиции):**
- 5: Идеальное совпадение должности + индустрии + уровня + Tier-1 компания
- 4: Совпадение должности, возможно другая индустрия
- 3: Смежная позиция, потребуется адаптация
- 2: Слабое совпадение, большой gap
- 1: Нерелевантно

**EXPERTISE (Глубина навыков):**
- 5: 90%+ навыков VERIFIED + измеримые достижения
- 4: 70%+ навыков, большинство verified
- 3: 50%+ навыков, часть unverified
- 2: <50% навыков или критические missing
- 1: Нет ключевых навыков

**TRAJECTORY (Карьерный рост):**
- 5: Явный рост (повышения, расширение scope, рост команды) + Tier-1
- 4: Стабильный рост с доказательствами
- 3: Горизонтальная карьера, без явного роста
- 2: Downgrade или хаотичные переходы
- 1: Деградация или огромные пробелы

**STABILITY (Риски):**
- 5: Стабильная история, объяснимые переходы
- 4: Минимальные риски
- 3: Есть вопросы, требуют уточнения
- 2: Yellow flags (необъяснённые пробелы, частые смены без логики)
- 1: Red flags (нереалистичный опыт, явные несоответствия)

### ШАГ 3: СВЕТОФОР
На основе оценок определи вердикт:
- 🟢 GREEN: Средняя оценка ≥4.0 — звонить в первую очередь
- 🟡 YELLOW: Средняя 3.0-3.9 — рассмотреть если нет зелёных
- 🔴 RED: Средняя <3.0 — не тратить время

---

## ФОРМАТ ОТВЕТА (JSON)

{{
    "verdict": "GREEN" | "YELLOW" | "RED",
    "verdict_reason": "Одно предложение: главная причина вердикта",

    "scores": {{
        "relevance": 1-5,
        "expertise": 1-5,
        "trajectory": 1-5,
        "stability": 1-5
    }},

    "skills_analysis": {{
        "verified": ["навык1 — подтверждён: использовал в проекте X", "навык2 — подтверждён: 3 года опыта в компании Y"],
        "unverified": ["навык3 — указан в Skills, но не упомянут в опыте"],
        "missing": ["навык4 — требуется по вакансии, отсутствует"],
        "bonus": ["навык5 — не требуется, но полезен"]
    }},

    "experience_summary": {{
        "total_years": число,
        "relevant_years": число,
        "last_position": "должность",
        "last_company": "компания",
        "tier1_companies": ["компания1"] или [],
        "career_direction": "growth" | "stable" | "decline" | "pivot"
    }},

    "salary_analysis": {{
        "candidate_net": число или null,
        "candidate_gross_estimated": число или null,
        "vacancy_range": "от - до",
        "match": "within_range" | "above" | "below" | "unknown",
        "comment": "краткий комментарий"
    }},

    "pros": [
        "КОНКРЕТНЫЙ факт из резюме: цитата или достижение",
        "Ещё факт с цифрами если есть"
    ],

    "cons": [
        "КОНКРЕТНЫЙ gap или риск из резюме",
        "Ещё минус если есть"
    ],

    "red_flags": ["Только серьёзные проблемы"] или [],
    "yellow_flags": ["Требуют уточнения на интервью"] или [],
    "green_flags": ["Tier-1 компания", "Измеримые достижения"] или [],

    "interview_questions": [
        "ПЕРСОНАЛИЗИРОВАННЫЙ вопрос по конкретному gap из резюме этого кандидата",
        "Вопрос про конкретный опыт/переход из резюме этого кандидата",
        "Технический вопрос по unverified навыку если есть"
    ],

    "summary_for_recruiter": "Одно предложение для превью: роль, X лет, ключевой плюс или риск",

    "reasoning": "2-3 предложения: почему такой вердикт, с отсылкой к конкретным фактам из резюме"
}}

---

## ПРАВИЛА КАЧЕСТВА

### Для pros/cons:
❌ ПЛОХО: "Хороший опыт", "Релевантные навыки", "Недостаточно опыта"
✅ ХОРОШО: "3 года в Яндексе на позиции Senior Python", "Нет опыта с Kubernetes (требуется по вакансии)"

### Для interview_questions:
❌ ПЛОХО: "Расскажите о себе", "Какие ваши сильные стороны?"
✅ ХОРОШО: "Вы указали опыт с Kafka — расскажите, какой throughput обрабатывали?", "Почему ушли из Сбера после 8 месяцев?"

### Для summary_for_recruiter:
❌ ПЛОХО: "Подходящий кандидат для рассмотрения"
✅ ХОРОШО: "Senior Python, 6 лет, ex-Яндекс, но нет K8s — потребуется онбординг"

### Для verified skills:
Навык считается verified если в описании работы есть:
- Прямое упоминание технологии + задача ("разработал API на FastAPI")
- Измеримый результат ("оптимизировал запросы SQL, ускорил в 3 раза")
- Контекст использования ("внедрил CI/CD на GitLab")
"""

    def _calculate_composite_score(self, scores: Dict[str, int]) -> Dict[str, Any]:
        """Расчёт композитного скора из оценок 1-5"""
        weights = {
            "relevance": 0.35,
            "expertise": 0.30,
            "trajectory": 0.20,
            "stability": 0.15
        }

        weighted_sum = 0
        for key, weight in weights.items():
            score = scores.get(key, 3)
            weighted_sum += score * weight

        rank_score = int((weighted_sum - 1) * 25)  # 1→0, 5→100

        if weighted_sum >= 4.0:
            tier = "A"
        elif weighted_sum >= 3.0:
            tier = "B"
        else:
            tier = "C"

        if rank_score >= 75:
            recommendation = "hire"
        elif rank_score >= 55:
            recommendation = "interview"
        elif rank_score >= 40:
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
        """Обогащение результата анализа v3.0"""
        scores = result.get("scores", {})

        if not scores:
            old_score = result.get("score", 50)
            return result

        # Расчёт композитного скора
        composite = self._calculate_composite_score(scores)

        result["rank_score"] = composite["rank_score"]
        result["tier"] = composite["tier"]
        result["recommendation"] = composite["recommendation"]

        # Обратная совместимость
        result["score"] = composite["rank_score"]

        # Расчёт match_percent на бэкенде (не доверяем AI математику!)
        skills_analysis = result.get("skills_analysis", {})
        verified = len(skills_analysis.get("verified", []))
        unverified = len(skills_analysis.get("unverified", []))
        missing = len(skills_analysis.get("missing", []))
        total_required = verified + missing

        if total_required > 0:
            # Verified = 100%, Unverified = 50% веса
            match_score = verified + (unverified * 0.5)
            result["skills_match"] = int((match_score / total_required) * 100)
        else:
            result["skills_match"] = 50

        result["experience_match"] = int(scores.get("relevance", 3) * 20)

        # Маппинг для совместимости
        result["matching_skills"] = skills_analysis.get("verified", [])
        result["skill_gaps"] = skills_analysis.get("missing", [])
        result["strengths"] = result.get("pros", [])
        result["weaknesses"] = result.get("cons", [])
        result["summary_one_line"] = result.get("summary_for_recruiter", "")

        # career_trajectory
        trajectory_score = scores.get("trajectory", 3)
        exp_summary = result.get("experience_summary", {})
        result["career_trajectory"] = exp_summary.get("career_direction", "stable")

        # Tier-1 компании
        result["tier1_companies"] = exp_summary.get("tier1_companies", [])

        return result

    async def analyze_resume(
        self,
        vacancy_data: Dict[str, Any],
        resume_data: Dict[str, Any],
        force_reanalysis: bool = False
    ) -> Dict[str, Any]:
        """Анализ резюме кандидата на соответствие вакансии v3.0"""
        start_time = time.time()

        try:
            cache_key = self._get_cache_key(vacancy_data, resume_data)

            if not force_reanalysis:
                cached_result = self._get_cached_analysis(cache_key)
                if cached_result:
                    logger.info(f"Результат анализа получен из кеша: {cache_key}")
                    return cached_result

            prompt = self._create_analysis_prompt(vacancy_data, resume_data)

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Ты — эксперт-рекрутер. Анализируй резюме детально и честно.
Отвечай ТОЛЬКО валидным JSON. Не добавляй markdown или комментарии.
Будь конкретен: цитируй факты из резюме, указывай цифры и компании."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2500,
                response_format={"type": "json_object"}
            )

            ai_response = response.choices[0].message.content

            try:
                analysis_result = json.loads(ai_response)
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга JSON ответа: {e}")
                logger.error(f"Ответ AI: {ai_response[:500]}")
                raise AIAnalysisError("Некорректный формат ответа от AI")

            analysis_result = self._enrich_analysis_result(analysis_result)

            processing_time = int((time.time() - start_time) * 1000)
            analysis_result.update({
                "ai_model": self.model,
                "ai_tokens_used": response.usage.total_tokens,
                "ai_cost_rub": self._calculate_cost(response.usage.total_tokens),
                "processing_time_ms": processing_time,
                "prompt_version": "3.0"
            })

            self._cache_analysis(cache_key, analysis_result)

            logger.info(
                f"AI анализ v3.0 завершен за {processing_time}ms, "
                f"токенов: {response.usage.total_tokens}, "
                f"verdict: {analysis_result.get('verdict', '?')}, "
                f"tier: {analysis_result.get('tier', '?')}"
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
        """Пакетный анализ резюме"""
        if len(resumes_data) > 10:
            raise AIAnalysisError("Максимум 10 резюме за раз")

        import asyncio

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

        tasks = [analyze_single(resume) for resume in resumes_data]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_results = [
            result for result in results
            if isinstance(result, dict) and "error" not in result
        ]

        logger.info(f"Пакетный анализ: {len(successful_results)}/{len(resumes_data)} успешно")

        return successful_results

    def _calculate_cost(self, total_tokens: int) -> float:
        """Расчет стоимости запроса в рублях"""
        # GPT-4o стоимость (примерно $2.5 input + $10 output за 1M токенов)
        # Средняя ~$5 за 1M токенов
        cost_per_1k_tokens_usd = 0.005
        cost_usd = (total_tokens / 1000) * cost_per_1k_tokens_usd
        cost_rub = cost_usd * 100  # Примерный курс
        return round(cost_rub, 2)

    async def get_analysis_stats(self) -> Dict[str, Any]:
        """Статистика использования AI анализатора"""
        return {
            "total_analyses": 0,
            "analyses_today": 0,
            "total_cost_rub": 0,
            "avg_score": 0,
            "cache_hit_rate": 0,
            "prompt_version": "3.0"
        }
