"""
AI сервис для анализа резюме v5.1
Интеграция с OpenAI GPT-4o для анализа кандидатов
Фокус: конкретные достижения, метрики, цифры
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
        return f"analysis:v5:{vh}:{rh}"

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
        """Построение промпта v5.1"""
        if isinstance(resume, str):
            resume = json.loads(resume) if resume else {}

        # Опыт работы
        exp_list = resume.get('experience', [])
        work_history = ""
        for i, exp in enumerate(exp_list[:5]):
            if isinstance(exp, dict):
                # company может быть dict или string
                company_raw = exp.get('company', '?')
                company = company_raw.get('name', '?') if isinstance(company_raw, dict) else (company_raw or '?')
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

        return f"""# РОЛЬ
Ты — скептичный аудитор с аллергией на bullshit.

Твои принципы:
- Нет цифр = нет достижения
- "Работал в компании X" — это не заслуга, это факт биографии
- Прилагательные ("успешный", "эффективный") = пустой звук
- Доверяй только глаголам с цифрами: "увеличил на 40%", "запустил 3 категории"
- Резюме без конкретики — это не скромность, это отсутствие результатов

Помни: лучше честный RED с объяснением, чем вежливый YELLOW ни о чём.

# ЗАДАЧА
Проанализируй кандидата для вакансии. Фокус на КОНКРЕТНЫХ ДОСТИЖЕНИЯХ и ЦИФРАХ.

# ВАКАНСИЯ
Позиция: {vacancy.get('title', '?')}
Требования: {v_skills or vacancy.get('description', '')[:500]}
Уровень: {vacancy.get('experience', '?')}
Бюджет: {sal_from} - {sal_to} RUB gross

# КАНДИДАТ
{resume.get('first_name', '')} {resume.get('last_name', '')} | {resume.get('title', '?')}
Опыт: {years} лет {rem} мес | Ожидания: {salary_gross} RUB gross

## Опыт работы:
{work_history or 'Не указан'}

## Сопроводительное:
{cover}

# АЛГОРИТМ АНАЛИЗА

## 1. ЧТО НУЖНО РАБОТОДАТЕЛЮ?
Выдели 3 главных задачи из вакансии.

## 2. ИЗВЛЕКИ МЕТРИКИ ИЗ РЕЗЮМЕ
⚠️ КРИТИЧЕСКИ ВАЖНО: Пиши цифру ТОЛЬКО если она ЯВНО указана в тексте.
ЗАПРЕЩЕНО угадывать, экстраполировать, округлять. Нет данных = null.

Ищи: объём (товары, заказы, клиенты), деньги (выручка, бюджет), рост (%), команда, инструменты.

## 3. УЧИТЫВАЙ АКТУАЛЬНОСТЬ
Приоритет — достижения за последние 2 года.
Результаты 3+ летней давности имеют меньший вес.

## 4. СОПОСТАВЬ С ПОТРЕБНОСТЯМИ
- Есть опыт с цифрами за 2 года → сильная сторона
- Есть опыт без цифр → требует уточнения
- Нет опыта → слабая сторона

## 5. ВЫВОД
"Почему СТОИТ/НЕ СТОИТ звать?" = факт, не мнение.

# ПРАВИЛА ФОРМУЛИРОВОК

ЗАПРЕЩЕНО: "успешный", "эффективный", "опытный", "крупный", "имеет опыт", "работал в", "знаком с", "подходит"
РАЗРЕШЕНО: глаголы ("увеличил", "запустил", "внедрил") + цифры ("выручка 2M", "500 SKU", "команда 5 чел")

❌ "Успешный опыт работы на маркетплейсе"
✅ "WB: увеличил выручку с 500K до 2M руб/мес за 8 мес"

❌ "Работал в крупной компании"
✅ "Ozon, 2023-2024 — цифры не указаны"

❌ "Отсутствие сопроводительного письма"
✅ "Не указана мотивация перехода"

# ФОРМАТ ОТВЕТА (только JSON)

{{
  "vacancy_needs": ["задача 1", "задача 2", "задача 3"],
  "candidate_metrics": [
    {{"name": "метрика", "value": "значение или null", "period": "2023-2024 или null"}},
    {{"name": "метрика", "value": "значение или null", "period": "null"}},
    {{"name": "метрика", "value": "значение или null", "period": "null"}}
  ],
  "verdict": "GREEN | YELLOW | RED",
  "verdict_reason": "Звонить/Уточнить/Отказ: [факт из резюме]",
  "scores": {{"relevance": 1-5, "experience_quality": 1-5, "recency": 1-5}},
  "pros": ["Глагол + цифра + контекст"],
  "cons": ["Пробел относительно вакансии"],
  "missing_info": ["Что уточнить на интервью"],
  "salary_fit": {{"status": "в бюджете | выше бюджета | ниже бюджета", "delta_percent": 0}},
  "interview_questions": ["Вопрос на проверку"]
}}"""

    def _calculate_score(self, scores: Dict[str, int]) -> Dict[str, Any]:
        # Новые веса для v5.1: relevance, experience_quality, recency
        weights = {"relevance": 0.45, "experience_quality": 0.35, "recency": 0.20}
        weighted = sum(scores.get(k, 3) * w for k, w in weights.items())
        rank = max(0, min(100, int((weighted - 1) * 25)))

        tier = "A" if weighted >= 4.0 else "B" if weighted >= 3.0 else "C"
        rec = "hire" if rank >= 75 else "interview" if rank >= 55 else "maybe" if rank >= 40 else "reject"

        return {"rank_score": rank, "tier": tier, "recommendation": rec, "weighted_average": round(weighted, 2)}

    def _enrich(self, result: Dict) -> Dict:
        """Обогащение результата v5.1"""
        scores = result.get("scores", {})
        if not scores:
            return result

        composite = self._calculate_score(scores)
        result.update(composite)
        result["score"] = composite["rank_score"]

        # Метрики кандидата — считаем заполненность
        metrics = result.get("candidate_metrics", [])
        filled = sum(1 for m in metrics if m.get("value") and m.get("value") != "null")
        result["metrics_filled"] = filled
        result["has_metrics"] = filled > 0

        # Совместимость со старым форматом для Excel
        result["strengths"] = result.get("pros", [])
        result["weaknesses"] = result.get("cons", [])
        result["summary_one_line"] = result.get("verdict_reason", "")

        # salary_fit — извлекаем статус
        sal = result.get("salary_fit", {})
        if isinstance(sal, dict):
            result["salary_status"] = sal.get("status", "—")
            result["salary_delta"] = sal.get("delta_percent", 0)
        else:
            result["salary_status"] = sal
            result["salary_delta"] = 0

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
                    {"role": "system", "content": "Отвечай ТОЛЬКО валидным JSON. Без markdown, без комментариев."},
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
                "prompt_version": "5.1"
            })

            self._set_cache(key, result)
            logger.info(f"AI v5.1: {result.get('verdict')} score={result.get('rank_score')} metrics={result.get('metrics_filled', 0)}/3 {resp.usage.total_tokens}tok")
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
