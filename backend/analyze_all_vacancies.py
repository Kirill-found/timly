"""
Запуск анализа для всех вакансий (response и consider, исключая discard)
Анализ выполняется отдельно для каждой вакансии
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.vacancy import Vacancy
from app.models.application import Application, AnalysisResult
from app.services.ai_analyzer import AIAnalyzer
from sqlalchemy import or_, and_, not_

async def analyze_vacancy(vacancy_id: str, vacancy_title: str):
    """Анализ всех неанализированных откликов для одной вакансии"""
    db = SessionLocal()

    try:
        # Найти неанализированные отклики (response и consider, БЕЗ discard)
        unanalyzed = db.query(Application).outerjoin(
            AnalysisResult,
            Application.id == AnalysisResult.application_id
        ).filter(
            Application.vacancy_id == vacancy_id,
            AnalysisResult.id == None,
            and_(
                or_(
                    Application.collection_id.like("%response%"),
                    Application.collection_id.like("%consider%")
                ),
                not_(Application.collection_id.like("%discard%"))
            )
        ).all()

        print(f'\n[START] Vacancy: {vacancy_title}')
        print(f'  Vacancy ID: {vacancy_id}')
        print(f'  Unanalyzed (response + consider): {len(unanalyzed)}')

        if not unanalyzed:
            print(f'  [OK] No applications to analyze\n')
            return

        # Разбивка по коллекциям
        response_count = sum(1 for app in unanalyzed if 'response' in app.collection_id)
        consider_count = sum(1 for app in unanalyzed if 'consider' in app.collection_id)

        print(f'    - response (new): {response_count}')
        print(f'    - consider (reviewing): {consider_count}')
        print()

        ai_analyzer = AIAnalyzer()
        successful = 0
        failed = 0

        for idx, application in enumerate(unanalyzed, 1):
            try:
                print(f'  [{idx}/{len(unanalyzed)}] Analyzing: {application.candidate_name}')

                # Получить данные вакансии
                vacancy = application.vacancy

                vacancy_data = {
                    "title": vacancy.title,
                    "description": vacancy.description,
                    "key_skills": vacancy.key_skills,
                    "experience": vacancy.experience,
                    "salary_from": vacancy.salary_from,
                    "salary_to": vacancy.salary_to,
                    "currency": vacancy.currency
                }

                # Анализ
                ai_result = await ai_analyzer.analyze_resume(
                    vacancy_data,
                    application.resume_data
                )

                if not ai_result:
                    print(f'    [ERROR] Empty AI result')
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

                print(f'    [OK] score={ai_result.get("score")}, recommendation={ai_result.get("recommendation")}')
                successful += 1

            except Exception as e:
                print(f'    [ERROR] {e}')
                failed += 1
                db.rollback()
                continue

        print(f'\n  [DONE] Vacancy: {vacancy_title}')
        print(f'    Successful: {successful}')
        print(f'    Failed: {failed}')
        print()

    finally:
        db.close()


async def main():
    db = SessionLocal()

    # Получить все вакансии
    vacancies = db.query(Vacancy).all()

    print('\n' + '='*80)
    print('         ANALYZING ALL VACANCIES (response + consider only)')
    print('='*80)

    for vacancy in vacancies:
        await analyze_vacancy(vacancy.id, vacancy.title)

    db.close()

    print('='*80)
    print('                    ALL VACANCIES ANALYZED')
    print('='*80 + '\n')


if __name__ == "__main__":
    asyncio.run(main())
