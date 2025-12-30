#!/usr/bin/env python3
"""Script to update export_analysis_to_excel function in analysis.py"""
import re

# Read the file
with open('/root/timly/backend/app/api/analysis.py', 'r', encoding='utf-8') as f:
    content = f.read()

# New function implementation
new_function = '''@router.get("/export/excel")
async def export_analysis_to_excel(
    vacancy_id: str,
    recommendation: Optional[str] = None,
    min_score: Optional[int] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Экспорт проанализированных откликов в Excel v2.0

    Структура файла:
    - Лист 1: Сводка (краткая таблица для быстрого просмотра)
    - Лист 2: Детальный анализ (полная информация по каждому кандидату)
    - Лист 3: Статистика (общие метрики)

    Параметры:
    - vacancy_id: ID вакансии (обязательный)
    - recommendation: Фильтр по рекомендации (hire, interview, maybe, reject)
    - min_score: Минимальный балл для фильтрации
    """
    try:
        from app.models.application import Application, AnalysisResult
        from app.models.vacancy import Vacancy
        from app.api.excel_export import create_excel_export
        from datetime import datetime
        from urllib.parse import quote

        # Проверка вакансии
        vacancy = db.query(Vacancy).filter(
            Vacancy.id == vacancy_id,
            Vacancy.user_id == current_user.id
        ).first()

        if not vacancy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "VACANCY_NOT_FOUND", "message": "Вакансия не найдена"}
            )

        # Базовый запрос результатов с фильтрацией
        query = db.query(AnalysisResult, Application).join(
            Application,
            AnalysisResult.application_id == Application.id
        ).filter(
            Application.vacancy_id == vacancy_id
        )

        if recommendation:
            query = query.filter(AnalysisResult.recommendation == recommendation)

        if min_score is not None:
            query = query.filter(AnalysisResult.score >= min_score)

        results = query.order_by(AnalysisResult.score.desc().nulls_last()).all()

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "NO_RESULTS", "message": "Нет проанализированных откликов"}
            )

        # Создание Excel файла через новый модуль v2.0
        file_path = create_excel_export(vacancy, results, recommendation)

        # Имя файла
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"timly_analysis_{timestamp}.xlsx"
        display_filename = f"timly_{vacancy.title}_{timestamp}.xlsx"
        encoded_filename = quote(display_filename)

        return FileResponse(
            file_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=safe_filename,
            headers={
                "Content-Disposition": f"attachment; filename={safe_filename}; filename*=UTF-8''{encoded_filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка экспорта в Excel: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "EXPORT_ERROR", "message": f"Ошибка экспорта: {str(e)}"}
        )


@router.get("/export/{export_job_id}/status"'''

# Pattern to find the old function (from @router.get("/export/excel") to next @router)
pattern = r'@router\.get\("/export/excel"\).*?(?=\n@router\.get\("/export/\{export_job_id\}/status")'
replacement = new_function

# Replace
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('/root/timly/backend/app/api/analysis.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated successfully!")
