"""
Сервис парсинга резюме из файлов
Поддерживает PDF и Excel форматы
Использует AI для извлечения структурированных данных
"""
import io
import json
import logging
import re
from typing import Dict, Any, List, Optional, BinaryIO
from datetime import datetime

# Ленивые импорты для тяжелых библиотек - импортируем только когда нужно
# import pdfplumber  # Lazy import
# import pandas as pd  # Lazy import
from openai import AsyncOpenAI

from app.config import settings
from app.utils.exceptions import FileParseError

logger = logging.getLogger(__name__)


class ResumeParser:
    """
    Универсальный парсер резюме
    Извлекает данные из PDF и Excel файлов
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def parse_pdf(self, file: BinaryIO, filename: str) -> Dict[str, Any]:
        """
        Парсинг PDF резюме

        Args:
            file: Файловый объект PDF
            filename: Имя файла

        Returns:
            Dict: Структурированные данные резюме
        """
        try:
            # Извлекаем текст из PDF
            text = self._extract_text_from_pdf(file)

            if not text or len(text.strip()) < 50:
                raise FileParseError("PDF файл пустой или не содержит текста")

            logger.info(f"Извлечено {len(text)} символов из PDF: {filename}")

            # AI парсинг текста в структуру
            parsed_data = await self._ai_parse_resume_text(text)
            parsed_data["original_text"] = text
            parsed_data["original_filename"] = filename
            parsed_data["source"] = "pdf"

            return parsed_data

        except Exception as e:
            logger.error(f"Ошибка парсинга PDF {filename}: {e}")
            raise FileParseError(f"Не удалось распарсить PDF: {e}")

    def _extract_text_from_pdf(self, file: BinaryIO) -> str:
        """Извлечение текста из PDF файла"""
        # Ленивый импорт pdfplumber - загружаем только когда нужно
        import pdfplumber

        text_parts = []

        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        return "\n\n".join(text_parts)

    async def parse_excel(self, file: BinaryIO, filename: str) -> List[Dict[str, Any]]:
        """
        Парсинг Excel файла с кандидатами

        Args:
            file: Файловый объект Excel
            filename: Имя файла

        Returns:
            List[Dict]: Список кандидатов
        """
        # Ленивый импорт pandas - загружаем только когда нужно
        import pandas as pd

        try:
            # Читаем Excel
            df = pd.read_excel(file)

            if df.empty:
                raise FileParseError("Excel файл пустой")

            logger.info(f"Прочитано {len(df)} строк из Excel: {filename}")

            # Автоматический маппинг колонок
            column_mapping = self._detect_column_mapping(df.columns.tolist())

            candidates = []
            for idx, row in df.iterrows():
                candidate = self._map_excel_row(row, column_mapping)
                candidate["original_filename"] = filename
                candidate["source"] = "excel"
                candidate["row_number"] = idx + 2  # +2 для заголовка и 0-индекса
                candidates.append(candidate)

            return candidates

        except Exception as e:
            logger.error(f"Ошибка парсинга Excel {filename}: {e}")
            raise FileParseError(f"Не удалось распарсить Excel: {e}")

    def _detect_column_mapping(self, columns: List[str]) -> Dict[str, str]:
        """
        Автоматическое определение соответствия колонок

        Args:
            columns: Список названий колонок

        Returns:
            Dict: Маппинг наших полей -> колонки Excel
        """
        mapping = {}
        columns_lower = [str(c).lower().strip() for c in columns]

        # Паттерны для определения колонок
        patterns = {
            "first_name": ["имя", "first_name", "firstname", "name", "фио"],
            "last_name": ["фамилия", "last_name", "lastname", "surname"],
            "email": ["email", "почта", "e-mail", "mail", "емейл"],
            "phone": ["телефон", "phone", "тел", "mobile", "мобильный"],
            "title": ["должность", "position", "title", "позиция", "вакансия"],
            "city": ["город", "city", "регион", "location", "area"],
            "salary": ["зарплата", "salary", "зп", "оклад", "ожидания"],
            "experience": ["опыт", "experience", "стаж", "exp"],
            "skills": ["навыки", "skills", "компетенции", "умения"],
            "age": ["возраст", "age", "год рождения", "дата рождения"],
        }

        for field, keywords in patterns.items():
            for i, col in enumerate(columns_lower):
                if any(kw in col for kw in keywords):
                    mapping[field] = columns[i]
                    break

        logger.info(f"Автоматический маппинг колонок: {mapping}")
        return mapping

    def _map_excel_row(self, row, mapping: Dict[str, str]) -> Dict[str, Any]:
        """Маппинг строки Excel в структуру кандидата"""
        import pandas as pd

        candidate = {}

        for field, column in mapping.items():
            value = row.get(column)
            if pd.notna(value):
                # Обработка разных типов
                if field == "skills" and isinstance(value, str):
                    # Разбиваем навыки по запятой или точке с запятой
                    candidate[field] = [s.strip() for s in re.split(r'[,;]', value) if s.strip()]
                elif field in ["salary", "age", "experience"]:
                    # Числовые поля
                    try:
                        candidate[field] = int(float(value))
                    except (ValueError, TypeError):
                        candidate[field] = None
                else:
                    candidate[field] = str(value).strip()

        return candidate

    async def _ai_parse_resume_text(self, text: str) -> Dict[str, Any]:
        """
        AI парсинг текста резюме в структурированные данные

        Args:
            text: Сырой текст резюме

        Returns:
            Dict: Структурированные данные
        """
        prompt = f"""Ты — AI парсер резюме. Извлеки структурированные данные из текста резюме.

## ТЕКСТ РЕЗЮМЕ:
{text[:6000]}  # Ограничиваем размер

## ЗАДАЧА:
Извлеки следующие данные и верни в формате JSON:

{{
    "first_name": "Имя (только имя, без фамилии)",
    "last_name": "Фамилия",
    "middle_name": "Отчество (если есть)",
    "email": "Email адрес",
    "phone": "Телефон (в формате +7...)",
    "title": "Желаемая должность / текущая должность",
    "age": число или null,
    "gender": "male/female или null",
    "city": "Город проживания",
    "salary_expectation": число (только цифры, без валюты) или null,
    "experience_years": число лет опыта или null,
    "experience_text": "Краткое описание опыта работы (2-3 предложения)",
    "skills": ["навык1", "навык2", "навык3", ...],
    "education": "Образование (вуз, специальность)"
}}

## ПРАВИЛА:
1. Извлекай ТОЛЬКО то, что явно указано в тексте
2. Если данных нет — ставь null
3. Телефон форматируй как +7XXXXXXXXXX
4. Навыки извлекай как массив строк
5. Возраст считай по году рождения если указан
6. Опыт в годах — общий стаж работы

Ответ строго в формате JSON без markdown."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты точный парсер данных. Отвечаешь только JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            logger.info(f"AI успешно распарсил резюме: {result.get('first_name')} {result.get('last_name')}")
            return result

        except Exception as e:
            logger.error(f"Ошибка AI парсинга: {e}")
            # Возвращаем минимальную структуру
            return {
                "first_name": None,
                "last_name": None,
                "email": None,
                "phone": None,
                "title": None,
                "skills": [],
                "parse_error": str(e)
            }

    async def analyze_candidate(
        self,
        candidate_data: Dict[str, Any],
        vacancy_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI анализ кандидата под вакансию

        Args:
            candidate_data: Данные кандидата
            vacancy_data: Данные вакансии

        Returns:
            Dict: Результат анализа
        """
        # Используем тот же формат что и в ai_analyzer.py
        prompt = f"""## ЗАДАЧА
Оцени соответствие кандидата вакансии и дай рекомендацию.

## ВАКАНСИЯ:
Название: {vacancy_data.get('title', 'Не указано')}
Требуемые навыки: {', '.join(vacancy_data.get('key_skills', [])) or 'Не указаны'}
Требуемый опыт: {vacancy_data.get('experience', 'Не указан')}
Зарплатная вилка: {vacancy_data.get('salary_from', 0)} - {vacancy_data.get('salary_to', 0)} {vacancy_data.get('currency', 'RUB')}

## КАНДИДАТ:
ФИО: {candidate_data.get('first_name', '')} {candidate_data.get('last_name', '')}
Должность: {candidate_data.get('title', 'Не указана')}
Город: {candidate_data.get('city', 'Не указан')}
Опыт: {candidate_data.get('experience_years', 'Не указан')} лет
Навыки: {', '.join(candidate_data.get('skills', [])) or 'Не указаны'}
Зарплатные ожидания: {candidate_data.get('salary_expectation', 'Не указаны')}
Опыт работы: {candidate_data.get('experience_text', 'Не указан')[:500]}

## ФОРМАТ ОТВЕТА (JSON):

{{
    "score": <число 0-100>,
    "skills_match": <число 0-100>,
    "experience_match": <число 0-100>,
    "salary_match": "<match/higher/lower/unknown>",
    "strengths": ["сильная сторона 1", "сильная сторона 2", "сильная сторона 3"],
    "weaknesses": ["слабая сторона 1", "слабая сторона 2"],
    "red_flags": ["красный флаг если есть"],
    "recommendation": "<hire/interview/maybe/reject>",
    "reasoning": "Краткое обоснование (2-3 предложения)"
}}

## ШКАЛА РЕКОМЕНДАЦИЙ:
- hire (90-100): Идеальный кандидат
- interview (70-89): Пригласить на собеседование
- maybe (50-69): Рассмотреть при нехватке лучших
- reject (0-49): Не подходит"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты эксперт HR аналитик. Отвечай только JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            result["analyzed_at"] = datetime.utcnow().isoformat()
            return result

        except Exception as e:
            logger.error(f"Ошибка AI анализа кандидата: {e}")
            return {
                "score": 0,
                "recommendation": "error",
                "reasoning": f"Ошибка анализа: {e}",
                "error": str(e)
            }
