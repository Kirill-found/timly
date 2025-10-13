"""
Сервис для анализа резюме с помощью AI (GPT-4o-mini)
"""
from openai import AsyncOpenAI
from typing import Dict, Any, List, Optional
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Анализатор резюме с использованием OpenAI GPT-4o-mini"""
    
    def __init__(self):
        """Инициализация клиента OpenAI"""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o-mini"  # Используем GPT-4o-mini для экономии
    
    async def analyze_resume(
        self,
        resume_data: Dict[str, Any],
        vacancy_data: Dict[str, Any],
        cover_letter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Анализ резюме кандидата относительно вакансии
        
        Args:
            resume_data: Данные резюме с HH.ru
            vacancy_data: Данные вакансии
            cover_letter: Сопроводительное письмо (если есть)
            
        Returns:
            Результат анализа
        """
        try:
            # Подготавливаем промпт для анализа
            prompt = self._create_analysis_prompt(resume_data, vacancy_data, cover_letter)
            
            # Отправляем запрос к GPT-4o-mini
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Ты опытный HR-специалист, который анализирует соответствие кандидатов вакансиям.
                        Твоя задача - объективно оценить кандидата и дать структурированный анализ.
                        Отвечай на русском языке. Будь объективным и конкретным."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Низкая температура для консистентности
                max_tokens=1500,
                response_format={"type": "json_object"}  # Форсируем JSON ответ
            )
            
            # Парсим ответ
            result = json.loads(response.choices[0].message.content)
            
            # Добавляем метаданные
            result["model_used"] = self.model
            result["tokens_used"] = response.usage.total_tokens if response.usage else 0
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при анализе резюме: {e}")
            return self._get_error_result(str(e))
    
    def _create_analysis_prompt(
        self,
        resume_data: Dict[str, Any],
        vacancy_data: Dict[str, Any],
        cover_letter: Optional[str]
    ) -> str:
        """
        Создание промпта для анализа
        
        Args:
            resume_data: Данные резюме
            vacancy_data: Данные вакансии
            cover_letter: Сопроводительное письмо
            
        Returns:
            Промпт для GPT
        """
        # Извлекаем ключевую информацию из резюме
        resume_info = self._extract_resume_info(resume_data)
        vacancy_info = self._extract_vacancy_info(vacancy_data)
        
        prompt = f"""
        Проанализируй соответствие кандидата вакансии.
        
        ВАКАНСИЯ:
        Название: {vacancy_info['title']}
        Описание: {vacancy_info['description']}
        Требования: {vacancy_info['requirements']}
        Зарплата: {vacancy_info['salary']}
        
        КАНДИДАТ:
        Имя: {resume_info['name']}
        Возраст: {resume_info['age']}
        Опыт работы: {resume_info['experience']}
        Образование: {resume_info['education']}
        Навыки: {resume_info['skills']}
        О себе: {resume_info['about']}
        Желаемая зарплата: {resume_info['salary']}
        
        """
        
        if cover_letter:
            prompt += f"\nСОПРОВОДИТЕЛЬНОЕ ПИСЬМО:\n{cover_letter}\n"
        
        prompt += """
        Верни JSON объект со следующей структурой:
        {
            "score": число от 0 до 100 (общая оценка соответствия),
            "summary": "краткое резюме анализа (2-3 предложения)",
            "strengths": ["список сильных сторон кандидата для этой вакансии"],
            "weaknesses": ["список слабых сторон или несоответствий"],
            "recommendation": "рекомендация: пригласить на интервью / отказать / требует дополнительной проверки",
            "key_skills_match": {
                "matched": ["навыки которые есть у кандидата"],
                "missing": ["навыки которых не хватает"]
            },
            "experience_analysis": "анализ опыта работы относительно требований",
            "salary_match": "соответствие зарплатных ожиданий",
            "risks": ["потенциальные риски при найме"]
        }
        """
        
        return prompt
    
    def _extract_resume_info(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Извлечение ключевой информации из резюме
        
        Args:
            resume_data: Сырые данные резюме с HH.ru
            
        Returns:
            Структурированная информация
        """
        info = {
            "name": resume_data.get("first_name", "") + " " + resume_data.get("last_name", ""),
            "age": resume_data.get("age", "не указан"),
            "experience": [],
            "education": [],
            "skills": [],
            "about": resume_data.get("skills", ""),
            "salary": "не указана"
        }
        
        # Извлекаем опыт работы
        for exp in resume_data.get("experience", []):
            exp_text = f"{exp.get('position', '')} в {exp.get('company', '')} ({exp.get('start', '')} - {exp.get('end', 'настоящее время')})"
            if exp.get("description"):
                exp_text += f": {exp.get('description')}"
            info["experience"].append(exp_text)
        
        # Извлекаем образование
        for edu in resume_data.get("education", {}).get("primary", []):
            edu_text = f"{edu.get('name', '')} - {edu.get('organization', '')}"
            info["education"].append(edu_text)
        
        # Извлекаем навыки
        info["skills"] = resume_data.get("skill_set", [])
        
        # Зарплатные ожидания
        if resume_data.get("salary"):
            salary = resume_data["salary"]
            info["salary"] = f"{salary.get('amount', '')} {salary.get('currency', '')}"
        
        return info
    
    def _extract_vacancy_info(self, vacancy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Извлечение ключевой информации из вакансии
        
        Args:
            vacancy_data: Сырые данные вакансии
            
        Returns:
            Структурированная информация
        """
        info = {
            "title": vacancy_data.get("name", ""),
            "description": vacancy_data.get("description", ""),
            "requirements": vacancy_data.get("key_skills", []),
            "salary": "не указана"
        }
        
        # Зарплата
        if vacancy_data.get("salary"):
            salary = vacancy_data["salary"]
            salary_from = salary.get("from", "")
            salary_to = salary.get("to", "")
            currency = salary.get("currency", "")
            
            if salary_from and salary_to:
                info["salary"] = f"{salary_from} - {salary_to} {currency}"
            elif salary_from:
                info["salary"] = f"от {salary_from} {currency}"
            elif salary_to:
                info["salary"] = f"до {salary_to} {currency}"
        
        return info
    
    def _get_error_result(self, error_message: str) -> Dict[str, Any]:
        """
        Возврат результата с ошибкой
        
        Args:
            error_message: Сообщение об ошибке
            
        Returns:
            Результат с ошибкой
        """
        return {
            "score": 0,
            "summary": f"Ошибка анализа: {error_message}",
            "strengths": [],
            "weaknesses": [],
            "recommendation": "Требуется ручная проверка",
            "error": True,
            "error_message": error_message
        }