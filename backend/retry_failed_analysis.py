"""
Скрипт для повторного анализа неуспешных резюме
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.application import Application, AnalysisResult
from app.services.ai_analyzer import AIAnalyzer
from sqlalchemy import select

async def retry_failed_analyses(vacancy_id: str):
    db = SessionLocal()

    try:
        # Находим неанализированные отклики
        unanalyzed = db.query(Application).outerjoin(
            AnalysisResult,
            Application.id == AnalysisResult.application_id
        ).filter(
            Application.vacancy_id == vacancy_id,
            Application.collection_id.like('%response%'),
            AnalysisResult.id == None
        ).all()

        print(f"Найдено неанализированных резюме: {len(unanalyzed)}")

        if not unanalyzed:
            print("Нет резюме для анализа")
            return

        ai_analyzer = AIAnalyzer()
        successful = 0
        failed = 0

        for idx, application in enumerate(unanalyzed, 1):
            try:
                print(f"\n[{idx}/{len(unanalyzed)}] Анализируем: {application.candidate_name}")

                vacancy_data = {
                    "title": application.vacancy.title,
                    "description": application.vacancy.description,
                    "key_skills": application.vacancy.key_skills,
                    "experience": application.vacancy.experience,
                    "salary_from": application.vacancy.salary_from,
                    "salary_to": application.vacancy.salary_to,
                    "currency": application.vacancy.currency
                }

                # Анализ
                ai_result = await ai_analyzer.analyze_resume(
                    vacancy_data,
                    application.resume_data
                )

                if not ai_result:
                    print(f"  [ERROR] Пустой результат анализа")
                    failed += 1
                    continue

                # Сохранение
                analysis_result = AnalysisResult(
                    application_id=application.id,
                    score=ai_result.get("score"),
                    skills_match=ai_result.get("skills_match"),
                    experience_match=ai_result.get("experience_match"),
                    salary_match=ai_result.get("salary_match"),
                    strengths=ai_result.get("strengths", []),
                    weaknesses=ai_result.get("weaknesses", []),
                    red_flags=ai_result.get("red_flags", []),
                    recommendation=ai_result.get("recommendation"),
                    reasoning=ai_result.get("reasoning"),
                    ai_model=ai_result.get("ai_model"),
                    ai_tokens_used=ai_result.get("ai_tokens_used"),
                    ai_cost_rub=ai_result.get("ai_cost_rub"),
                    processing_time_ms=ai_result.get("processing_time_ms")
                )

                db.add(analysis_result)
                db.commit()

                print(f"  [OK] Успешно: score={ai_result.get('score')}, recommendation={ai_result.get('recommendation')}")
                successful += 1

            except Exception as e:
                print(f"  [ERROR] Ошибка: {e}")
                failed += 1
                db.rollback()
                continue

        print(f"\n\nИтого:")
        print(f"  Успешно: {successful}")
        print(f"  Неудачно: {failed}")

    finally:
        db.close()

if __name__ == "__main__":
    vacancy_id = "e18cde91-5afc-4a9c-a837-113f476957fc"
    asyncio.run(retry_failed_analyses(vacancy_id))
