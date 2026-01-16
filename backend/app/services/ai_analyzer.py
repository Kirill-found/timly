"""
AI сервис для анализа резюме v6.0-lite
Интеграция с OpenAI GPT-4o для анализа кандидатов
Фокус: категоризация позиций, GHOST_SKILL детекция, прозрачный скоринг
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
    def __init__(self):
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)

        import httpx
        http_client = None
        if hasattr(settings, 'OPENAI_PROXY_URL') and settings.OPENAI_PROXY_URL:
            http_client = httpx.AsyncClient(
                proxies={"http://": settings.OPENAI_PROXY_URL, "https://": settings.OPENAI_PROXY_URL},
                timeout=90.0
            )

        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, http_client=http_client)
        self.model = settings.OPENAI_MODEL

        try:
            self.cache = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=5)
            self.cache.ping()
        except Exception as e:
            logger.warning(f"Redis недоступен: {e}")
            self.cache = None

    def _get_cache_key(self, vacancy_data: Dict, resume_data: Dict) -> str:
        vh = hashlib.md5(json.dumps(vacancy_data, sort_keys=True).encode()).hexdigest()[:8]
        rh = hashlib.md5(json.dumps(resume_data, sort_keys=True).encode()).hexdigest()[:8]
        return f"analysis:v60:{vh}:{rh}"

    def _get_cached(self, key: str) -> Optional[Dict]:
        if not self.cache:
            return None
        try:
            cached = self.cache.get(key)
            return json.loads(cached) if cached else None
        except:
            return None

    def _set_cache(self, key: str, result: Dict, ttl: int = 86400):
        if self.cache:
            try:
                self.cache.setex(key, ttl, json.dumps(result, ensure_ascii=False))
            except:
                pass

    def _build_prompt(self, vacancy: Dict, resume: Dict, strictness: str = "balanced") -> str:
        """Построение промпта v6.0-lite"""
        if isinstance(resume, str):
            resume = json.loads(resume) if resume else {}

        # Опыт работы
        exp_list = resume.get('experience', [])
        work_history = ""
        for i, exp in enumerate(exp_list[:5]):
            if isinstance(exp, dict):
                company_raw = exp.get('company', '?')
                company = company_raw.get('name', '?') if isinstance(company_raw, dict) else (company_raw or '?')
                pos = exp.get('position', '?')
                desc = exp.get('description', '') or ''
                start = exp.get('start')
                end = exp.get('end')
                if isinstance(start, dict):
                    period_start = f"{start.get('month', '')}/{start.get('year', '')}"
                elif isinstance(start, str):
                    period_start = start[:7] if len(start) >= 7 else start
                else:
                    period_start = '?'
                if isinstance(end, dict):
                    period_end = f"{end.get('month', '')}/{end.get('year', '')}"
                elif isinstance(end, str):
                    period_end = end[:7] if len(end) >= 7 else end
                else:
                    period_end = 'н.в.'
                period = f"{period_start} - {period_end}"
                work_history += f"\n### {company} | {pos} | {period}\n{desc}\n"

        # Навыки (список)
        skills = []
        for s in resume.get('skill_set', []):
            skills.append(s.get('name', '') if isinstance(s, dict) else s)
        skills_text = ', '.join(skills) or 'Не указаны'

        # Зарплата кандидата (NET → GROSS)
        salary_data = resume.get('salary')
        salary = salary_data.get('amount', 0) if isinstance(salary_data, dict) else 0
        salary_gross = int(salary * 1.15) if salary else 0

        # Общий опыт
        exp_data = resume.get('total_experience')
        months = exp_data.get('months', 0) if isinstance(exp_data, dict) else 0
        months = months or 0
        years, rem = months // 12, months % 12

        # Локация кандидата
        candidate_area = resume.get('area', {})
        candidate_city = candidate_area.get('name', '?') if isinstance(candidate_area, dict) else str(candidate_area or '?')

        # Готовность к переезду
        relocation = resume.get('relocation', {})
        relocation_ready = relocation.get('type', {}).get('id', '') if isinstance(relocation, dict) else ''
        relocation_text = "готов к переезду" if relocation_ready == 'relocation_possible' else "не готов к переезду"

        # Сопроводительное письмо
        cover = resume.get('cover_letter', '') or resume.get('message', '') or 'Не указано'

        # Вакансия
        v_skills = ', '.join(vacancy.get('key_skills', [])) or 'Не указаны'
        v_description = vacancy.get('description', '')[:800] if vacancy.get('description') else ''
        sal_from = vacancy.get('salary_from', 0) or 0
        sal_to = vacancy.get('salary_to', 0) or 0
        v_area = vacancy.get('area', '?')

        return f"""# РОЛЬ

Ты — алгоритм первичного скрининга резюме. Не HR с мнением, а система с чёткой логикой.

Твоя задача: определить, стоит ли рекрутеру тратить 15 минут на звонок этому кандидату.

Принципы:
1. Факты > мнения. Оценивай только написанное, не додумывай.
2. Навык в списке ≠ опыт с навыком. Проверяй в описании работы.
3. Разные позиции — разная логика оценки.
4. Лучше лишний YELLOW, чем ложный GREEN.

---

# ШАГ 1: ОПРЕДЕЛИ ТИП ПОЗИЦИИ

| Тип | Кто | Как оценивать |
|-----|-----|---------------|
| RESULTS | Продажи, маркетинг, закупки, e-commerce, менеджеры МП | Цифры важны. Нет цифр = уточнить |
| EXPERTISE | Разработка, аналитика, дизайн, инженеры | Глубина навыков > цифры. Проверяй в опыте |
| OPERATIONS | Водители, склад, операторы, бухгалтеры | Стаж + допуски. Цифры не важны |
| COMMUNICATION | HR, поддержка, ассистенты, PR | Контекст (B2B/B2C) + soft skills |

---

# ШАГ 2: БЛОКИРУЮЩИЕ ПРОВЕРКИ

## 2.1 Локация
- Вакансия: {v_area}
- Кандидат: {candidate_city}, {relocation_text}
- Если формат работы требует присутствия, а кандидат в другом городе и не готов к переезду → RED

## 2.2 MUST-HAVE требования
Извлеки 2-4 критичных требования из вакансии.
Для каждого определи статус:
- ✅ CONFIRMED — есть в опыте с доказательством
- ⚠️ UNCLEAR — возможно есть, нужно уточнить
- ❌ MISSING — нет

**Любой MUST-HAVE = MISSING → автоматический RED**

---

# ШАГ 3: ПРОВЕРКА НАВЫКОВ

⚠️ Навык в блоке "Skills" — заявка. Факт — упоминание в описании опыта.

| В навыках | В опыте | Статус | Флаг |
|-----------|---------|--------|------|
| ✅ | ✅ с контекстом | VERIFIED | — |
| ✅ | ❌ или без контекста | MENTIONED | GHOST_SKILL |
| ❌ | ✅ | VERIFIED | — |
| ❌ | ❌ | MISSING | — |

**GHOST_SKILL** = навык-призрак. Указан в списке, но не используется в описании опыта.
- 1-2 призрака → вопросы на интервью
- 3+ призрака в ключевых навыках → понижение вердикта

---

# ШАГ 4: СКОРИНГ

## Формула:
total = (MUST_HAVE × 0.40) + (RELEVANCE × 0.30) + (QUALITY × 0.20) + (OTHER × 0.10)

## MUST_HAVE (40%):
- Все CONFIRMED → 100
- Один UNCLEAR → 70
- Любой MISSING → 0

## RELEVANCE (30%):
- Идентичная роль + индустрия → 100
- Похожая роль ИЛИ другая индустрия → 70
- Смежный опыт с пересечением задач → 50
- Косвенно релевантный → 30
- Нерелевантный → 0

## QUALITY (20%) — зависит от типа позиции:
- RESULTS: Есть цифры → 100, Факты без цифр → 60, Только обязанности → 30
- EXPERTISE: Навыки VERIFIED → 100, Есть GHOST_SKILL → 50, Не подтверждены → 20
- OPERATIONS: Стаж 3+ лет, стабильно → 100, 1-3 года → 70, Частая смена → 30
- COMMUNICATION: Похожий контекст → 100, Частично похож → 60, Другой контекст → 30

## OTHER (10%):
- Зарплата в вилке → +30
- Зарплата +1-20% выше → +15
- Зарплата +20-30% → 0
- Зарплата +30%+ → -20
- Nice-to-have навыки → до +40

---

# ШАГ 5: ФЛАГИ

## Красные (понижают вердикт на ступень):
- 3+ смены работы за 2 года без причины
- Зарплата +30% при score <70
- 3+ GHOST_SKILL в ключевых навыках
- Деградация позиций (Senior → Junior)

## Жёлтые (добавляют вопросы, не меняют вердикт):
- Gap >6 месяцев
- Короткий срок на последнем месте (<6 мес)
- Overqualified
- 1-2 GHOST_SKILL

---

# ШАГ 6: ВЕРДИКТ

| Score | Вердикт | Значение |
|-------|---------|----------|
| 70-100 | GREEN | Звонить. Высокая вероятность соответствия |
| 45-69 | YELLOW | Есть потенциал, нужно уточнить |
| 0-44 | RED | Не звонить. Явное несоответствие |

---

# ВАКАНСИЯ
Позиция: {vacancy.get('title', '?')}
Локация: {v_area}
Требования: {v_skills}
Описание: {v_description}
Зарплата: {sal_from} - {sal_to} RUB gross

# КАНДИДАТ
{resume.get('first_name', '')} {resume.get('last_name', '')} | {resume.get('title', '?')}
Локация: {candidate_city} | {relocation_text}
Опыт: {years} лет {rem} мес
Ожидания: {salary_gross} RUB gross

## Навыки (из блока Skills):
{skills_text}

## Опыт работы:
{work_history or 'Не указан'}

## Сопроводительное:
{cover}

---

# ТРЕБОВАНИЯ К КАЧЕСТВУ АНАЛИЗА

⚠️ КРИТИЧЕСКИ ВАЖНО:

**Strengths — только КОНКРЕТИКА:**
- Указывай КОМПАНИИ где работал (Ozon, WB, ООО Рога и Копыта)
- Указывай ПЕРИОДЫ (2 года, 6 месяцев)
- Указывай ЦИФРЫ если есть (5М оборот, 1000 SKU)
- НЕ ПИШИ общие фразы "опыт работы с X", "длительный опыт"

**Concerns — тоже КОНКРЕТИКА:**
- Указывай ЧТО ИМЕННО не так
- "Последние 2 года бухгалтер в ООО Ромашка — не МП"
- "Gap 8 месяцев между Альфа и Бета"
- НЕ ПИШИ "нет релевантного опыта" без деталей

**Interview questions — УМНЫЕ:**
- Вопрос должен проверять конкретное сомнение
- "Расскажите про работу с Ozon в компании X" — хорошо
- "Расскажите про ваш опыт" — плохо

---

# ФОРМАТ ОТВЕТА (только JSON)

{{
  "position_type": "RESULTS | EXPERTISE | OPERATIONS | COMMUNICATION",

  "location_check": {{
    "compatible": true,
    "flag": null,
    "reason": null
  }},

  "must_have": [
    {{"requirement": "...", "status": "CONFIRMED|UNCLEAR|MISSING", "evidence": "цитата или null"}}
  ],

  "skills_check": [
    {{"skill": "...", "status": "VERIFIED|MENTIONED|MISSING", "ghost": false, "evidence": "..."}}
  ],

  "scoring": {{
    "must_have": {{"score": 0, "reason": "..."}},
    "relevance": {{"score": 0, "reason": "..."}},
    "quality": {{"score": 0, "reason": "..."}},
    "other": {{"score": 0, "reason": "..."}},
    "total": 0,
    "flags_applied": null
  }},

  "verdict": "GREEN | YELLOW | RED",
  "verdict_reason": "Одно предложение — главная причина",

  "strengths": [
    "КОНКРЕТНЫЕ факты из резюме с деталями (компании, цифры, периоды)",
    "❌ НЕ ПИШИ: 'Опыт работы с маркетплейсами'",
    "❌ НЕ ПИШИ: 'Длительный опыт в e-commerce'",
    "✅ ПИШИ: '2 года менеджером МП в Ozon (ООО Селлер Про)'",
    "✅ ПИШИ: 'Рост оборота с 2М до 5М за 6 мес в компании X'"
  ],
  "concerns": [
    "КОНКРЕТНЫЕ факты, которые вызывают сомнения",
    "❌ НЕ ПИШИ: 'Нет релевантного опыта'",
    "✅ ПИШИ: 'Последние 3 года работал бухгалтером, не МП'"
  ],

  "salary_fit": {{
    "status": "в вилке | выше на X% | ниже | не указано",
    "impact": 0
  }},

  "interview_questions": [
    {{
      "question": "...",
      "why": "что проверяем",
      "good_answer": "что хотим услышать",
      "bad_answer": "что насторожит"
    }}
  ]
}}"""

    def _calculate_score(self, scoring: Dict) -> int:
        """Вычисление итогового score из компонентов v6.0"""
        must_have = scoring.get("must_have", {}).get("score", 0)
        relevance = scoring.get("relevance", {}).get("score", 0)
        quality = scoring.get("quality", {}).get("score", 0)
        other = scoring.get("other", {}).get("score", 0)

        total = int(must_have * 0.40 + relevance * 0.30 + quality * 0.20 + other * 0.10)
        return max(0, min(100, total))

    def _enrich(self, result: Dict) -> Dict:
        """Обогащение результата v6.0"""

        # Пересчитываем score если нужно
        scoring = result.get("scoring", {})
        if scoring and not scoring.get("total"):
            scoring["total"] = self._calculate_score(scoring)
            result["scoring"] = scoring

        # Основной score для сортировки
        result["score"] = scoring.get("total", 0) if scoring else 0
        result["rank_score"] = result["score"]

        # Recommendation на основе вердикта
        verdict = result.get("verdict", "YELLOW")
        result["recommendation"] = {
            "GREEN": "interview",
            "YELLOW": "maybe",
            "RED": "reject"
        }.get(verdict, "maybe")

        # Tier для совместимости
        score = result["score"]
        result["tier"] = "A" if score >= 70 else "B" if score >= 45 else "C"

        # Совместимость со старым форматом для Excel и фронтенда
        result["pros"] = result.get("strengths", [])
        result["cons"] = result.get("concerns", [])
        result["weaknesses"] = result.get("concerns", [])
        result["summary_one_line"] = result.get("verdict_reason", "")

        # Бары для фронтенда (skills_match, experience_match)
        result["skills_match"] = scoring.get("must_have", {}).get("score", 0)
        result["experience_match"] = scoring.get("relevance", {}).get("score", 0)

        # Ghost skills count
        skills_check = result.get("skills_check", [])
        ghost_count = sum(1 for s in skills_check if s.get("ghost"))
        result["ghost_skills_count"] = ghost_count
        result["has_ghost_skills"] = ghost_count > 0

        # Must-have status
        must_have = result.get("must_have", [])
        missing_count = sum(1 for m in must_have if m.get("status") == "MISSING")
        unclear_count = sum(1 for m in must_have if m.get("status") == "UNCLEAR")
        result["must_have_missing"] = missing_count
        result["must_have_unclear"] = unclear_count

        # Salary fit
        sal = result.get("salary_fit", {})
        if isinstance(sal, dict):
            result["salary_status"] = sal.get("status", "—")
            result["salary_delta"] = sal.get("impact", 0)
        else:
            result["salary_status"] = str(sal) if sal else "—"
            result["salary_delta"] = 0

        # Position type
        result["position_type"] = result.get("position_type", "RESULTS")

        return result

    async def analyze_resume(self, vacancy: Dict, resume: Dict, force: bool = False, strictness: str = "balanced") -> Dict:
        """
        Анализ резюме v6.0-lite
        """
        start = time.time()
        key = self._get_cache_key(vacancy, resume)

        if not force:
            cached = self._get_cached(key)
            if cached:
                return cached

        prompt = self._build_prompt(vacancy, resume, strictness)

        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Отвечай ТОЛЬКО валидным JSON. Без markdown, без комментариев."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2500,
                response_format={"type": "json_object"}
            )

            result = json.loads(resp.choices[0].message.content)
            result = self._enrich(result)
            result.update({
                "ai_model": self.model,
                "ai_tokens": resp.usage.total_tokens,
                "processing_ms": int((time.time() - start) * 1000),
                "prompt_version": "6.0"
            })

            self._set_cache(key, result)

            ghost = result.get("ghost_skills_count", 0)
            logger.info(f"AI v6.0: {result.get('verdict')} score={result.get('score')} type={result.get('position_type')} ghosts={ghost} {resp.usage.total_tokens}tok")
            return result

        except openai.RateLimitError:
            raise AIAnalysisError("Rate limit OpenAI")
        except Exception as e:
            logger.error(f"AI error: {e}")
            raise AIAnalysisError(str(e))

    async def analyze_batch(self, vacancy: Dict, resumes: List[Dict], max_concurrent: int = 3) -> List[Dict]:
        import asyncio
        sem = asyncio.Semaphore(max_concurrent)

        async def one(r):
            async with sem:
                try:
                    return await self.analyze_resume(vacancy, r)
                except Exception as e:
                    return {"error": str(e), "resume_id": r.get("id")}

        results = await asyncio.gather(*[one(r) for r in resumes[:10]])
        return [r for r in results if "error" not in r]
