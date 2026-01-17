"""
AI сервис для анализа резюме v7.0 (Hybrid Expert)
Интеграция с OpenAI GPT-4o для анализа кандидатов
Подход: Must-haves валидация + Холистическая оценка
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
        return f"analysis:v72:{vh}:{rh}"

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
        """Построение промпта v7.0 (Hybrid Expert)"""
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
        v_description = vacancy.get('description', '')[:1200] if vacancy.get('description') else ''
        sal_from = vacancy.get('salary_from', 0) or 0
        sal_to = vacancy.get('salary_to', 0) or 0
        v_area = vacancy.get('area', '?')

        return f"""# РОЛЬ

Ты — Senior Recruiter с 15-летним опытом найма. Твоя задача — оценить кандидата так, как это сделал бы опытный HR: целостно, с пониманием контекста, а не по чеклисту.

## ПРИНЦИПЫ ОЦЕНКИ

1. **Понимание вакансии важнее ключевых слов**
   - Сначала пойми, КАКОЙ человек нужен на эту позицию
   - Какие задачи он будет решать? Какой контекст?
   - Что критично, а что можно освоить?

2. **Холистическая оценка кандидата**
   - Смотри на карьерный путь целиком, не только последнее место
   - Оценивай КАЧЕСТВО опыта, не только наличие ключевых слов
   - Ищи паттерны: рост, стабильность, достижения

3. **Релевантность важнее формального соответствия**
   - Опыт в смежной нише может быть ценнее, чем слабый опыт в целевой
   - Человек, который вырастил магазин с 0 до 5М в одежде, может быть лучше того, кто "работал с оборудованием" без результатов

4. **Здравый смысл над правилами**
   - Если что-то не указано — это не автоматический минус
   - Контекст определяет важность факторов

---

# ПОРЯДОК АНАЛИЗА (выполняй строго по шагам)

## ШАГ 1: АНАЛИЗ ВАКАНСИИ

Прочитай вакансию и ответь себе:
- Какой ТИП работы? (операционка / развитие / запуск с нуля)
- Какая НИША и её специфика? (технический товар? fashion? FMCG?)
- Что КРИТИЧНО для успеха на этой позиции?
- Что можно ОСВОИТЬ за 1-2 месяца?

Выдели 2-4 MUST-HAVE требования — то, БЕЗ ЧЕГО кандидат не справится:
- Это должны быть реальные стоп-факторы, а не wish-list
- Пример must-have: "Опыт работы с WB от 1 года" — да
- Пример НЕ must-have: "Знание Excel" — это осваивается за неделю

## ШАГ 2: ПРОВЕРКА СТОП-ФАКТОРОВ

Для каждого must-have определи статус:
- ✅ ЕСТЬ — подтверждено в опыте работы
- ❓ ВОЗМОЖНО — похожий опыт, нужно уточнить
- ❌ НЕТ — явно отсутствует или противоречит

⚠️ **КРИТИЧЕСКОЕ ПРАВИЛО:**
Если хотя бы один must-have = ❌ НЕТ → вердикт ОБЯЗАН быть "Mismatch"
Это правило НЕ МОЖЕТ быть переопределено никакими плюсами кандидата.

## ШАГ 3: ХОЛИСТИЧЕСКИЙ АНАЛИЗ

Если стоп-факторы пройдены, оцени кандидата целостно:

**Сильные стороны (ищи конкретику):**
- Где работал? (названия компаний)
- Сколько? (периоды)
- Что делал? (задачи)
- Чего достиг? (цифры, если есть)
- Какой карьерный тренд? (рост/стагнация)

**Риски и сомнения:**
- Частая смена работы?
- Gaps в карьере?
- Деградация позиций?
- Несоответствие ожиданий по зарплате?
- Нет подтверждения заявленных навыков?

**Релевантность опыта:**
- Прямой опыт в нише? → сильный плюс
- Смежный опыт с похожими задачами? → хороший плюс
- Опыт с другим товаром, но на тех же площадках? → нормально
- Совсем другой опыт? → риск

## ШАГ 4: ВЕРДИКТ

| Вердикт | Когда ставить |
|---------|---------------|
| **Mismatch** | Хотя бы один must-have отсутствует. Не тратьте время |
| **Low** | Must-haves формально есть, но слабые. Много сомнений. Только если некого больше |
| **Medium** | Есть потенциал, но нужно уточнить ключевые моменты на интервью |
| **High** | Сильное соответствие. Рекомендую связаться в приоритете |

---

# ВАКАНСИЯ

**Позиция:** {vacancy.get('title', '?')}
**Локация:** {v_area}
**Зарплата:** {sal_from} - {sal_to} RUB gross

**Требования:**
{v_skills}

**Описание:**
{v_description}

---

# КАНДИДАТ

**{resume.get('first_name', '')} {resume.get('last_name', '')}**
Желаемая позиция: {resume.get('title', '?')}
Локация: {candidate_city} | {relocation_text}
Общий опыт: {years} лет {rem} мес
Ожидания по зарплате: {salary_gross} RUB gross

**Навыки (заявленные):**
{skills_text}

**Опыт работы:**
{work_history or 'Не указан'}

**Сопроводительное письмо:**
{cover}

---

# ФОРМАТ ОТВЕТА (только валидный JSON)

{{
  "vacancy_analysis": {{
    "position_type": "operations | growth | launch",
    "niche_specifics": "краткое описание специфики ниши",
    "what_critical": "что критично для успеха",
    "what_learnable": "что можно освоить"
  }},

  "must_haves": [
    {{
      "requirement": "формулировка требования",
      "status": "yes | maybe | no",
      "evidence": "цитата из резюме или null",
      "reasoning": "почему такой статус"
    }}
  ],

  "holistic_analysis": {{
    "career_summary": "2-3 предложения о карьерном пути кандидата",
    "relevance_assessment": "насколько опыт релевантен этой вакансии и почему",
    "growth_pattern": "растёт | стабилен | деградирует | непонятно"
  }},

  "strengths": [
    "КОНКРЕТНОЕ достижение или навык, подтверждённый опытом (не просто 'работал в компании X')",
    "Пример: 'Вырастил оборот магазина с 2М до 8М за 1.5 года в Детский мир'"
  ],

  "concerns": [
    "УНИКАЛЬНОЕ сомнение (не дублируй одно и то же разными словами)",
    "Не повторяй информацию из salary_fit здесь"
  ],

  "verdict": "Mismatch | Low | Medium | High",

  "priority": "top | strong | basic",

  "one_liner": "ОДНО предложение (максимум 20 слов): почему ЭТОТ кандидат и чем он ОТЛИЧАЕТСЯ. Конкретика: цифры, компании, достижения. Пример: 'WB 3 года, вырастила оборот с 2М до 12М — лучший опыт среди откликнувшихся'",

  "reasoning_for_hr": "Развёрнутое объяснение для HR (3-5 предложений). Включи: 1) Главное преимущество, 2) Релевантный опыт с конкретикой, 3) Основные риски. Пиши полными предложениями БЕЗ ОБРЫВОВ.",

  "interview_questions": [
    {{
      "question": "ПЕРСОНАЛИЗИРОВАННЫЙ вопрос именно для ЭТОГО кандидата, основанный на его конкретных пробелах или сомнениях из резюме. НЕ общие вопросы типа 'расскажите о себе'",
      "checks": "Конкретно что выясняем: 'Реальный ли опыт с WB или только упоминание в резюме'"
    }}
  ],

  "salary_fit": {{
    "status": "в вилке | выше на X% | ниже | не указано",
    "comment": "краткий комментарий (НЕ дублируй в concerns)"
  }}
}}

⚠️ ПРАВИЛА ПРИОРИТЕТА (priority):
- "top" = ВСЕ must-haves подтверждены (yes) + есть ИЗМЕРИМЫЕ достижения (цифры роста/выручки) + карьера растёт
- "strong" = ВСЕ must-haves подтверждены + хороший релевантный опыт, но без wow-достижений
- "basic" = must-haves есть, но некоторые "maybe" ИЛИ есть существенные concerns

⚠️ ПРАВИЛА КАЧЕСТВА:
1. one_liner — ОДНО короткое предложение с КОНКРЕТИКОЙ (цифры, компании). НЕ общие слова типа "хороший опыт"
2. НЕ дублируй информацию между полями
3. strengths — ДОСТИЖЕНИЯ с цифрами, а не "работал в компании X"
4. interview_questions — ПЕРСОНАЛИЗИРОВАННЫЕ под пробелы этого кандидата

⚠️ ЖЕЛЕЗНОЕ ПРАВИЛО: Если любой must_have имеет status="no" → verdict="Mismatch", priority="basic"."""

    def _enrich(self, result: Dict) -> Dict:
        """Обогащение результата v7.2 с приоритетом"""

        verdict = result.get("verdict", "Low")
        priority = result.get("priority", "basic")

        # Маппинг verdict + priority → score для сортировки
        # High: top=95, strong=85, basic=75
        # Medium: 55-65
        # Low: 35-45
        # Mismatch: 15
        score_map = {
            ("High", "top"): 95,
            ("High", "strong"): 85,
            ("High", "basic"): 75,
            ("Medium", "top"): 65,
            ("Medium", "strong"): 58,
            ("Medium", "basic"): 52,
            ("Low", "top"): 45,
            ("Low", "strong"): 40,
            ("Low", "basic"): 35,
            ("Mismatch", "top"): 15,
            ("Mismatch", "strong"): 15,
            ("Mismatch", "basic"): 15,
        }
        result["score"] = score_map.get((verdict, priority), 50)
        result["rank_score"] = result["score"]

        # Recommendation на основе вердикта
        result["recommendation"] = {
            "High": "interview",
            "Medium": "maybe",
            "Low": "maybe",
            "Mismatch": "reject"
        }.get(verdict, "maybe")

        # Tier для совместимости
        result["tier"] = {
            "High": "A",
            "Medium": "B",
            "Low": "C",
            "Mismatch": "C"
        }.get(verdict, "B")

        # Совместимость со старым форматом для Excel и фронтенда
        result["pros"] = result.get("strengths", [])
        result["cons"] = result.get("concerns", [])
        result["weaknesses"] = result.get("concerns", [])
        result["summary_one_line"] = result.get("verdict_reason", "")

        # Бары для фронтенда
        holistic = result.get("holistic_analysis", {})
        relevance_text = holistic.get("relevance_assessment", "") if isinstance(holistic, dict) else ""

        # Примерная оценка для баров на основе вердикта
        if verdict == "High":
            result["skills_match"] = 85
            result["experience_match"] = 85
        elif verdict == "Medium":
            result["skills_match"] = 65
            result["experience_match"] = 60
        elif verdict == "Low":
            result["skills_match"] = 40
            result["experience_match"] = 35
        else:  # Mismatch
            result["skills_match"] = 20
            result["experience_match"] = 15

        # Must-have status
        must_haves = result.get("must_haves", [])
        missing_count = sum(1 for m in must_haves if m.get("status") == "no")
        unclear_count = sum(1 for m in must_haves if m.get("status") == "maybe")
        result["must_have_missing"] = missing_count
        result["must_have_unclear"] = unclear_count

        # Salary fit
        sal = result.get("salary_fit", {})
        if isinstance(sal, dict):
            result["salary_status"] = sal.get("status", "—")
        else:
            result["salary_status"] = str(sal) if sal else "—"

        # Position type
        va = result.get("vacancy_analysis", {})
        result["position_type"] = va.get("position_type", "operations") if isinstance(va, dict) else "operations"

        # Ghost skills - не используется в v7.0, но оставляем для совместимости
        result["ghost_skills_count"] = 0
        result["has_ghost_skills"] = False

        return result

    async def analyze_resume(self, vacancy: Dict, resume: Dict, force: bool = False, strictness: str = "balanced") -> Dict:
        """
        Анализ резюме v7.0 (Hybrid Expert)
        С retry логикой для rate limit
        """
        import asyncio
        start = time.time()
        key = self._get_cache_key(vacancy, resume)

        if not force:
            cached = self._get_cached(key)
            if cached:
                return cached

        prompt = self._build_prompt(vacancy, resume, strictness)

        # Retry с exponential backoff
        max_retries = 5
        base_delay = 2  # секунды

        for attempt in range(max_retries):
            try:
                resp = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Ты опытный HR-эксперт. Отвечай ТОЛЬКО валидным JSON. Без markdown, без комментариев."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.4,
                    max_tokens=2500,
                    response_format={"type": "json_object"}
                )

                result = json.loads(resp.choices[0].message.content)
                result = self._enrich(result)
                result.update({
                    "ai_model": self.model,
                    "ai_tokens": resp.usage.total_tokens,
                    "processing_ms": int((time.time() - start) * 1000),
                    "prompt_version": "7.0"
                })

                self._set_cache(key, result)

                logger.info(f"AI v7.0: {result.get('verdict')} score={result.get('score')} missing={result.get('must_have_missing')} {resp.usage.total_tokens}tok")
                return result

            except openai.RateLimitError as e:
                delay = base_delay * (2 ** attempt)  # 2, 4, 8, 16, 32 секунды
                if attempt < max_retries - 1:
                    logger.warning(f"Rate limit hit, retry {attempt + 1}/{max_retries} after {delay}s")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Rate limit after {max_retries} retries")
                    raise AIAnalysisError("Rate limit OpenAI - исчерпаны retry")
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
