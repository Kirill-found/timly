"""
AI сервис для анализа резюме v4.3
Интеграция с OpenAI GPT-4o для анализа кандидатов
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

TIER1_COMPANIES = [
    "яндекс", "yandex", "сбер", "sber", "тинькофф", "tinkoff", "t-bank",
    "вк", "vk", "mail.ru", "avito", "авито", "ozon", "озон",
    "wildberries", "вайлдберриз", "lamoda", "циан", "cian",
    "google", "гугл", "meta", "facebook", "amazon", "microsoft", "apple",
    "netflix", "uber", "spotify", "airbnb", "stripe", "shopify",
    "касперский", "kaspersky", "jetbrains", "miro",
    "revolut", "wise", "альфа-банк", "райффайзен", "втб",
    "mckinsey", "bcg", "bain", "deloitte", "pwc", "kpmg", "accenture",
]


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
        return f"analysis:v4:{vh}:{rh}"

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

    def _detect_tier1(self, text: str) -> List[str]:
        text_lower = text.lower()
        return list(set([c for c in TIER1_COMPANIES if c in text_lower]))

    def _build_prompt(self, vacancy: Dict, resume: Dict, strictness: str = "balanced") -> str:
        """Построение промпта v4.4"""
        if isinstance(resume, str):
            resume = json.loads(resume) if resume else {}

        # Опыт работы
        exp_list = resume.get('experience', [])
        work_history = ""
        companies = []
        for i, exp in enumerate(exp_list[:5]):
            if isinstance(exp, dict):
                # company может быть dict или string
                company_raw = exp.get('company', '?')
                company = company_raw.get('name', '?') if isinstance(company_raw, dict) else (company_raw or '?')
                companies.append(company)
                pos = exp.get('position', '?')
                desc = exp.get('description', '') or ''
                # start/end могут быть dict {"month": 1, "year": 2022} или string "2022-01-01"
                start = exp.get('start')
                end = exp.get('end')
                if isinstance(start, dict):
                    period_start = f"{start.get('month', '')}/{start.get('year', '')}"
                elif isinstance(start, str):
                    period_start = start[:7] if len(start) >= 7 else start  # "2022-01"
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

        tier1 = self._detect_tier1(work_history + ' '.join(companies))
        tier1_flag = f"⭐ TIER-1: {', '.join(tier1)}" if tier1 else ""

        # Навыки
        skills = []
        for s in resume.get('skill_set', []):
            skills.append(s.get('name', '') if isinstance(s, dict) else s)
        skills_text = ', '.join(skills) or 'Не указаны'

        # Зарплата (NET → GROSS) - может быть dict или None
        salary_data = resume.get('salary')
        salary = salary_data.get('amount', 0) if isinstance(salary_data, dict) else 0
        salary_gross = int(salary * 1.15) if salary else 0

        # Опыт - может быть dict или None
        exp_data = resume.get('total_experience')
        months = exp_data.get('months', 0) if isinstance(exp_data, dict) else 0
        months = months or 0  # защита от None
        years, rem = months // 12, months % 12

        # Junior mode
        title_lower = vacancy.get('title', '').lower()
        is_junior = any(w in title_lower for w in ['junior', 'джуниор', 'стажер', 'trainee', 'intern'])
        junior_flag = "🎓 JUNIOR MODE: Активен" if is_junior else ""

        # Cover letter
        cover = resume.get('cover_letter', '') or resume.get('message', '') or 'Не указано'

        # Вакансия
        v_skills = ', '.join(vacancy.get('key_skills', [])) or 'Не указаны'
        sal_from = vacancy.get('salary_from', 0) or 0
        sal_to = vacancy.get('salary_to', 0) or 0

        # Режим строгости
        strictness_instructions = {
            "strict": "РЕЖИМ: STRICT. Штрафуй за отсутствие цифр и достижений. Unverified навык = жёлтый флаг. Требуй доказательства.",
            "balanced": "РЕЖИМ: BALANCED. Ищи баланс между фактами и потенциалом. Давай шанс если есть косвенные подтверждения.",
            "lenient": "РЕЖИМ: LENIENT. Фокус на стабильности и мотивации. Прощай отсутствие деталей если общий профиль адекватен."
        }
        strictness_text = strictness_instructions.get(strictness, strictness_instructions["balanced"])

        return f"""# ROLE
Ты — беспристрастный HR-аудитор с 15-летним стажем.
Твоя задача: дать объективную оценку, найти факты и несоответствия.
Ты не веришь словам без доказательств, но и не ищешь причины отказать.

{strictness_text}

# ВХОДНЫЕ ДАННЫЕ

## ВАКАНСИЯ
Позиция: {vacancy.get('title', '?')}
Требуемый стек: {v_skills}
Уровень: {vacancy.get('experience', '?')}
Локация: {vacancy.get('area', '?')} | Формат: {vacancy.get('schedule', '?')}
Бюджет: {sal_from} - {sal_to} RUB gross
{junior_flag}

## КАНДИДАТ
Имя: {resume.get('first_name', '')} {resume.get('last_name', '')}
Текущая позиция: {resume.get('title', '?')}
Общий опыт: {years} лет {rem} мес
Локация: {resume.get('area', {}).get('name', '?') if isinstance(resume.get('area'), dict) else '?'}
Ожидания: {salary_gross} RUB gross
{tier1_flag}

### Навыки: {skills_text}

### Опыт работы:
{work_history or 'Не указан'}

### Сопроводительное письмо:
{cover}

# ОБЯЗАТЕЛЬНЫЕ ШАГИ АНАЛИЗА

## Шаг 0: PAIN POINTS ВАКАНСИИ
Выдели 3 ключевых вызова этой вакансии. Весь анализ веди через призму: «Решит ли кандидат эти проблемы?»

## Шаг 1: SKILL PROVENANCE
| Категория | Критерий |
|-----------|----------|
| verified | Навык + контекст (задача, результат) |
| contextual | Senior в своей области 2+ года → базовый инструментарий роли verified |
| unverified | Заявлен, но не подтверждён опытом |
| missing | Отсутствует |

## Шаг 2: ROLE INFLATION
- Tier-1 компания → доверяй должности
- Нет данных о масштабе → "insufficient_data", НЕ гадай
- "Lead" без команды = Senior, "CTO стартапа" без команды = разработчик

## Шаг 3: STABILITY + CONTEXT
Декрет, релокация, учёба = НЕ риск. Пробел >1 года БЕЗ причины = риск.

## Шаг 4: OVERQUALIFIED CHECK
Опыт 2x+ требований? Ищи причину в Cover Letter. Есть → YELLOW, нет → RED.

## Шаг 5: MOTIVATION CHECK
Персонализированное письмо = 5, шаблон = 2, пусто = 1.

{"## Шаг 6: JUNIOR MODE" + chr(10) + "Pet-проекты = 0.5x опыта. Оценивай потенциал и обучаемость." if is_junior else ""}

# SCORING RUBRIC (1-5)
| Критерий | Вес | Описание |
|----------|-----|----------|
| relevance | 35% | Закрывает ли pain points? 5 = "делал это вчера" |
| quality | 30% | Компании, рост, достижения |
| stability | 15% | С учётом контекста |
| motivation | 20% | Качество отклика |

**НЕ считай итоговый score.**

# КАЧЕСТВО ОТВЕТА

STOP-WORDS (запрещено): "хороший кандидат", "подходит", "соответствует", "рекомендуется", "имеет опыт"

## ФОРМАТ PROS (обязательно с цифрами/фактами):
❌ "Опыт работы на WB"
✅ "[Wildberries, 2 года] — рост GMV на 40%, работа с 500+ SKU"
❌ "Работал в крупной компании"
✅ "[Яндекс, Senior] — highload 10k RPS, команда 5 человек"

## ФОРМАТ CONS (фиксированные категории):
Используй ТОЛЬКО эти категории: [Опыт], [Навыки], [Мотивация], [Стабильность], [Зарплата], [Данные]
❌ "[Риск] — отсутствие письма"
✅ "[Мотивация] — нет сопроводительного письма, непонятна причина отклика"
❌ "[Мотивация] — отсутствие сопроводительного"
✅ "[Опыт] — нет подтверждённой работы с маркетплейсами"

# OUTPUT FORMAT

**Верни ТОЛЬКО JSON:**

{{
  "vacancy_pain_points": ["вызов1", "вызов2", "вызов3"],
  "verdict": "GREEN | YELLOW | RED",
  "verdict_reason": "Одна фраза для менеджера — почему да/нет",
  "scores": {{"relevance": 1-5, "quality": 1-5, "stability": 1-5, "motivation": 1-5}},
  "skills": {{
    "verified": ["навык — Компания: контекст"],
    "contextual": ["навык — причина"],
    "unverified": ["навык"],
    "missing": ["навык"]
  }},
  "experience_summary": {{
    "total_years": число,
    "relevant_years": число,
    "best_company": "название или null",
    "role_inflation": "none | minor | major | insufficient_data"
  }},
  "pros": ["[Компания, срок/роль] — конкретное достижение с цифрами"],
  "cons": ["[Опыт|Навыки|Мотивация|Стабильность|Зарплата|Данные] — конкретная проблема"],
  "red_flags": [],
  "yellow_flags": [],
  "salary_fit": "в бюджете | выше бюджета | ниже рынка",
  "is_overqualified": false,
  "overqualified_reason": null,
  "interview_questions": ["Вопрос на слабое место", "Вопрос на unverified навык"]
}}"""

    def _calculate_score(self, scores: Dict[str, int]) -> Dict[str, Any]:
        weights = {"relevance": 0.35, "quality": 0.30, "stability": 0.15, "motivation": 0.20}
        weighted = sum(scores.get(k, 3) * w for k, w in weights.items())
        rank = max(0, min(100, int((weighted - 1) * 25)))

        tier = "A" if weighted >= 4.0 else "B" if weighted >= 3.0 else "C"
        rec = "hire" if rank >= 75 else "interview" if rank >= 55 else "maybe" if rank >= 40 else "reject"

        return {"rank_score": rank, "tier": tier, "recommendation": rec, "weighted_average": round(weighted, 2)}

    def _enrich(self, result: Dict) -> Dict:
        scores = result.get("scores", {})
        if not scores:
            return result

        composite = self._calculate_score(scores)
        result.update(composite)
        result["score"] = composite["rank_score"]

        skills = result.get("skills", {})
        v = len(skills.get("verified", []))
        c = len(skills.get("contextual", []))
        m = len(skills.get("missing", []))
        total = v + c + m
        result["skills_match"] = int((v + c * 0.8) / total * 100) if total else 50

        # Совместимость
        result["matching_skills"] = skills.get("verified", []) + skills.get("contextual", [])
        result["skill_gaps"] = skills.get("missing", [])
        result["strengths"] = result.get("pros", [])
        result["weaknesses"] = result.get("cons", [])
        result["summary_one_line"] = result.get("verdict_reason", "")

        return result

    async def analyze_resume(self, vacancy: Dict, resume: Dict, force: bool = False, strictness: str = "balanced") -> Dict:
        """
        strictness: "strict" | "balanced" | "lenient"
        - strict: для топовых позиций, требует доказательств
        - balanced: стандартный режим (по умолчанию)
        - lenient: для массового найма, фокус на адекватности
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
                    {"role": "system", "content": "Ты — скептичный рекрутер. Отвечай ТОЛЬКО JSON. Без markdown."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            result = json.loads(resp.choices[0].message.content)
            result = self._enrich(result)
            result.update({
                "ai_model": self.model,
                "ai_tokens": resp.usage.total_tokens,
                "processing_ms": int((time.time() - start) * 1000),
                "prompt_version": "4.4"
            })

            self._set_cache(key, result)
            logger.info(f"AI v4.4: {result.get('verdict')} score={result.get('rank_score')} {resp.usage.total_tokens}tok")
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
